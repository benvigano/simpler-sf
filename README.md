# simpler-sf
Extending the low-level Salesforce API client [Simple Salesforce](https://github.com/simple-salesforce/simple-salesforce) to support exports in Pandas, and other features.

## Usage
### Install
`pip install simpler-sf`

### Import
```python
import simpler_sf
simpler_sf.simple_salesforce()
import simple_salesforce
# That's it!
```
### Query
Simpler-sf adds the `smart_query()` method to the `simple_salesforce.Salesforce` class.

The advantages over the existing methods are:
- Query results in `pd.Dataframe` format
- Un-nesting of results for relationship queries (aka the infamous `'attributes'` dictionary) 
- No limit on the number of output rows as in `simple_salesforce.Salesforce.query()` **and** at the same time...
- No need to use a different class for each Salesforce object as in `sf.bulk.Account.query(query)`
- The option to filter dynamically, on large amounts of values without a limit on the number of characters

#### Example
```python 
sf = simple_salesforce.Salesforce(username=username, password=password, security_token=token)
df = sf.smart_query('SELECT Id, FirstName, Account.Name FROM Contact')
print(df)
```
Output:
```
                    Id    FirstName   Account.Name
0   0032400000QZbmtAAD        Emily         Amazon
1   0032400000eGqdZAAS      Jasmine         Amazon
2   00324036u9QZbnGAAT         Míng      Microsoft
3   0032400000QZbygAAX    Magdalena         Google
```
