import pandas as pd
from collections.abc import Mapping
import math
from tqdm import tqdm
import re


def _recursive_unnest(data, parent_path='', results={}):
    '''Recursively un-nest records'''
    for current_level_key in data:
        path = '.'.join(filter(None, [parent_path, current_level_key]))
        if isinstance(data[current_level_key], Mapping) and "attributes" in data[current_level_key]:
            results = _recursive_unnest(data[current_level_key], path, results)
        else:
            if current_level_key != "attributes":
                results[path] = data[current_level_key]
            else:
                pass
    return results


def _unnest_query_output(records) -> dict:
    '''
    Un-nests the records.
    For relationship queries Salesforce returns nested results.
    '''

    blank_filler = "-"

    # Store the unnested records in a dictionary
    results = {}

    for record in records:
        unnested_record = _recursive_unnest(record)
        
        # Get the row index, to know how many blank fillers
        # to insert in case a new field is found
        if len(results.keys()) != 0:
            row_ix = len(results[list(results.keys())[0]])
        else:
            row_ix = 0

        '''
        Notice: when a record has a nan value, that field is not included in the record dictionary

        If the record has a field that wasn't present in the previous records,
        insert as many blank fillers as the number of previous records.
        Note: in the first iteration this will just write in 'results' an empty list for each field.
        '''
        for key in unnested_record:
            if key not in list(results.keys()):
                results[key] = [blank_filler] * row_ix

        for key in results:
            # If the key is present in this record
            if key in unnested_record:
                # And if it's not null
                if unnested_record[key] is not None:
                    # Append it's value to its list inside 'results' 
                    results[key].append(unnested_record[key])
                # If it's present but null
                else:
                    # Append a blank filler to its list inside 'results'
                    results[key].append(blank_filler)
            # If this record doesn't contatain this key
            else:
                # Append a blank filler to its list inside 'results'
                results[key].append(blank_filler)

    return results


def _determine_object(query):
    '''Parse a query to determine the Salesforce object'''

    if " from " not in query.lower():
        raise Exception(f"'FROM' statement not found in query '{query.lower()}'")

    return re.split(" from ", query, flags=re.IGNORECASE)[1].split(" ")[0]


def _determine_fields(query):
    '''Parse a query to determine the fields'''
    
    before_from = re.split(" from ", query, flags=re.IGNORECASE)[0]
    after_select = re.split("select ", before_from, flags=re.IGNORECASE)[1]
    fields = set(after_select.replace(" ", "").split(","))
    
    return fields


def _generate_sub_queries(query, filter_field, filter_values, not_in):
    '''
    Split the input query in multiple sub-queries that respect Salesforce 10,000 character limit.
    If the input query already respects the character limit, the function returns a list containing just the input query.
    '''
    
    query_character_limit = 100000  # As per SalesForce documentation
    
    if not_in:
        not_str = "NOT "
    else:
        not_str = ""
    
    # 14 is the length of the "WHERE..." part
    # 30 is for tolerance
    base_query_length = len(query) + 14 + len(filter_field) + 30
                    
    # Calculate min number of batches (OPTIMIZABLE!)
    longest_string_in_filter_values_list = max(filter_values, key=len)
    
    # "+4" is for comma and ''
    body_length = len(filter_values) * (len(longest_string_in_filter_values_list) + 4)
    
    slice_length = query_character_limit - base_query_length
    
    batches_number = math.ceil(body_length / slice_length)
    
    def _split_list(a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    # Split queries
    filter_values_batches = _split_list(filter_values, batches_number)
    
    # Generate the sub queries
    sub_queries = []
    for batch in filter_values_batches:
        if "WHERE" not in query:
            sub_queries.append(query + f"\nWHERE {filter_field} {not_str}IN {str(batch).replace('[', '(').replace(']', ')')}")

        else:
            before_where, after_where = re.split("where", query, flags=re.IGNORECASE)
            sub_queries.append(before_where + f"WHERE {filter_field} {not_str}IN {str(batch).replace('[', '(').replace(']', ')')}\nAND" + after_where)

    return sub_queries


def _smart_query(
    self,
    query: str,
    show_progress: [bool] = True,
    filter_field: str = None,
    filter_values: [object] = None,
    not_in: bool = False
    ):
    '''
    Parameters
        query: str,
        show_progress: [bool] (default: True),
        filter_field: str (default: None) : The field in 'WHERE -field- IN -values-',
        filter_values: [object] (default: None) : The values in 'WHERE -field- IN -values-',
        not_in: bool (default: False): If true, filter becomes 'WHERE -field- NOT IN -values-

    Returns
        pd.DataFrame
    '''
    
    # Make the query inline to ease parsing
    query = " ".join(line.strip() for line in query.splitlines())
    
    # Determine the Salesforce object by parsing the query
    object_name = _determine_object(query)
    object = getattr(self.bulk, object_name)

    # Determine the fields by parsing the query
    fields = _determine_fields(query)

    if filter_field is not None and filter_values is not None:
        sub_queries = _generate_sub_queries(query, filter_field, filter_values, not_in)
    else:
        sub_queries = [query]
                 
    dfs = []
    for sub_query in tqdm(sub_queries) if len(sub_queries) > 1 else sub_queries:
        results = _unnest_query_output(object.query(sub_query))    
        partial_df = pd.DataFrame(results)
        dfs.append(partial_df)
        
    output_df = pd.concat(dfs)
        
    # If the query didn't output any records, add the columns for output consistency
    if output_df.shape[0] == 0:
        output_df = pd.DataFrame(columns=list(fields))
    else:
        pass

    '''
    Remove any unrequested columns that were returned, accounting for case insensitivitiy and optional object name prefix
    This can happen for example in the query "SELECT Account.Id FROM Contact", infact
    if contacts that are not linked to an account are present, the additional column "Account" is returned.
    '''
    fields_lower = [f.lower() for f in fields]
    unrequested_columns = [c for c in output_df.columns if c.lower() not in fields_lower and object_name.lower() + "." + c.lower() not in fields_lower]
    output_df.drop(columns=unrequested_columns, inplace=True)
                    
    return output_df


def simple_salesforce():
    import simple_salesforce
    simple_salesforce.Salesforce.smart_query = _smart_query
