test_queries = \
    {
        """SELECT Name, Id FROM Account WHERE Id = '3r78th103487thq8137'""": "Account",

        """
        SELECT Name, Id FROM
        Account WHERE Id = '3r78th103487thq8137'
        """: "Account",

        """
        SELECT Name, Id FROM
        Contact
        LIMIT 10'
        """: "Contact",

        """
        SELECT Name, Id FROM Account
        """: "Account",

        """
        select Name, Id from Account where Id = '3r78th103487thq8137'
        """: "Account",

        """
        SELECT Name, Id From
        Contact
        LIMIT 10'
        """: "Contact",

        """
        SELECT Name, Id
        From Account
        LIMIT 10'
        """: "Account"
    }
