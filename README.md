# Write up for Eneco BTO Data CODE assessment
Author: Rick de Harder

In order to run the python code some packages are required, these can be found in the requirements.txt

## Question 1 & 2:
Code: q1andq2.py

For these two questions I decided to use python and specifically the polars package as my tools. 
My approach to solving these questions was to first load the three files into a polars dataframe and to then write them directly to csv to enable easy quick visual analysis.

Based on the questions asked it was clear that the dataframes had to be joined and based on the visual analysis I was able to identify the columns that contained the join keys.

### Question 1 part 1: number of airports per country
To then answer which countries had the most and the least airports could then be answered by aggregation the combined dataset of country and airports on the country name and adding a count based on the number of airports in the country.

This led to the following result for the 3 countries with the most airports:

| Country       | Number of airports |
| ------------- | ------------------ |
| United States | 25170              |
| Brazil        | 5546               |
| Canada        | 2829               |

And to the following result for the 10 countries with the least airports:

| Country                        | Number of airports |
| ------------------------------ | ------------------ |
| British Indian Ocean Territory | 1                  |
| Mayotte                        | 1                  |
| Nauru                          | 1                  |
| Vatican City                   | 1                  |
| Curaçao                        | 1                  |
| Niue                           | 1                  |
| Sint Maarten                   | 1                  |
| Gambia                         | 1                  |
| Saint Barthélemy               | 1                  |
| Christmas Island               | 1                  |


But on closer inspection of the results, it showed that there were actually 14 countries with only 1 airport, so the bottom 10 are now somewhat arbitrarily selected, it would be best to show all 14 countries with only 1 airport, so below the other 4 countries with only 1 airport are shown.

| Country                 | Number of airports |
| ----------------------- | ------------------ |
| Cocos (Keeling) Islands | 1                  |
| Gibraltar               | 1                  |
| Jersey                  | 1                  |
| Norfolk Island          | 1                  |

### Question 1 part 2: the airport with the longest runway per country

This question was a bit harder to answer, but first I for sure had to combine the runway data with earlier created dataset that contained the airports per country.

After this it was a matter of getting the max runway length for all the airports within a country. For this I used the sql like window functionality within the polars library. I took the joined data and used a filter to only keep the row with the longest runway length whilst iterating over each country.

But on closer review of the results, it became clear that for some airports within a country the longest runway was equally long. So, it did not necessarily result into a single airport for each country. 

This could be an acceptable answer but if it were a requirement to only return a single airport for each country, then we could add other requirements. For example, if the length is equal we could look at the max width of each of the runways and check if this gives a single answer.

To perform this analysis we first had to fill some missing data entries within the dataframe as otherwise rows would go missing from the result set due to how polars handles comparisons between values and null values.

Even though the extra comparison on width did help to reduce the number of duplicate airports it didn't fully resolve it. So, if it were needed more conditions could be added, based on 'business' requirements.

### Question 2
To upload the result set to the azure storage account the data is first read to a bytes buffer to then be uploaded to the storage account using the azure-storage-blob library. Unfortunately, this code was running into authentication errors, which on closer inspection seems to be due to an expired SAS token. It seems to have expired by 2024-10-17, whilst I was trying to use in on 2024-11-23


## Question 3
Code: q3.py

Question 3 seemed simple enough, by iterating over the countries dataframe and invoking the api using the python requests library I could get all data for each country and append it to a list.

By adding a check on the statuscode it was possible as well to identify the countries that were in the csv dataset but not available in the api. In the end it was only one country missing: 'Côte d'Ivoire'.

In the second part I again used the request library to upload an empty txt file to the endpoint and by checking for status code 201 I could be sure of the succesfull operation.

## Question 4
In order to change the cron schedule I first connected to Bob's server by opening a terminal window (mac) and running the following command:
```
ssh bob@95.179.138.59
```
And then entering Bob's password. I then checked for running cron jobs with
```
crontab -l
```
and saw the running cron job, so I then opened the cron jobs file with command
```
crontab -e
```
And there I saw that there the default schedule was specified which meant that the api was invoked every minute. I then changed the entry so the job will run during office hours which I assumed to be from 9-5 from Monday to Friday.

Old entry:
```
* * * * * /home/bob/invoke_api.sh 2>&1 > /dev/null 
```
New entry:
```
* 9-16 * * 1-5 /home/bob/invoke_api.sh 2>&1 > /dev/null 
```

By listing the contents of the server using the ls command I found bob's cat picture and noted down the location. I then closed the ssh connection and used scp to download the file to my local pc using the following command:
```
scp bob@95.179.138.59:/home/bob/cat.jpeg ~/Users/rickdeharder/Pictures
```

## Question 5
Code: q5.sql

### part 1
To prove or disprove Larry's question I decided to write a SQL statement for which I had the following plan of attack:
1. Create a result set that contains all customer, invoices and invoice_lines
2. Combine this result set with the track and genre tables and create a result set that only contains distinct customer_ids, of customers that have bought at least one Jazz track. And 
3. Then create another result set that returns the total revenue per customer
4. Then combine the result set from step 3 and 4 to analyze the difference between Jazz and not Jazz customers.

Running the query showed that Larry's hypotheses was NOT true, as the average gross_revenue for non Jazz customers was slightly higher:

| Customer type | Avg gross revenue |
| ------------- | ----------------- |
| Jazz          | ≈ 38.96           |
| Not Jazz      | ≈ 40.06           |

### part 2
My advice to Larry would be to not use the LOWER() function in his query. This is at this point in time not only performing unnecessary extra calculations but it might also be interfering with the proper use of the index that has been created on the track.name column.

If the usage of lower() is absolutely necessary because for example we can't use input validation to make sure of the appropiate casing in the track name. Then my advice to Larry would be to ask the database administrator to create a new column in the table that contains the lower cased version of the track name and to then create a new index on that column.

If Larry would then use that column in his query the index should still be working correctly.

## Question 6
Code: q6.py

After looking at the string I realized it was a base64 encoded Json Web Token (JWT). These are usually used to identify an authenticated user. This enables things like SSO so that users don't constantly have to keep authenticating.

 Using python I split the input string in it's three parts (header, payload and signature) and then decoded these strings for further analysis.

This gave the following payload:
```
{
    "aud":"https://Eneco.onmicrosoft.com/ecsaz-apigee-odp-t",
    "iss":"https://sts.windows.net/eca36054-49a9-4731-a42f-8400670fc022/",
    "iat":1616416705,
    "nbf":1616416705,"exp":1616420605,
    "aio":"E2ZgYEg3Vdmf6hspv/uPMbff8/MCAA==",
    "appid":"1e0fb354-a78d-4f5b-9966-ed623a624599",
    "appidacr":"1",
    "idp":"https://sts.windows.net/eca36054-49a9-4731-a42f-8400670fc022/",
    "oid":"db6e89f9-db16-4252-9429-c4d5e48adabd",
    "rh":"0.AQUAVGCj7KlJMUekL4QAZw_AIlSzDx6Np1tPmWbtYjpiRZkFAAA.",
    "roles":["ReadWoonEnergie","ReadEneco","ReadOxxio","ReadEnecoBusiness","ReadAll"],
    "sub":"db6e89f9-db16-4252-9429-c4d5e48adabd", subject
    "tid":"eca36054-49a9-4731-a42f-8400670fc022",
    "uti":"SgBa7Q3KTUy3Qf8hzOY3AA","ver":"1.0"
}
```

By analyzing this payload I think we can conclude that Bob is successfully logged in, this is for example shown by the roles he has.

These roles are of particular interest in this case because I assume these to be relevant for Role Based Access Control within Eneco. His read permissions seem to be quite broadly configured because of the ReadAll role. 

I therefore assume that there is an issue with how the permissions based on the roles are checked within the API and not necessarily with Bob's roles.

So I would therefore first doublecheck if the RBAC is configured correctly within the newly developed API.

## Question 7: 
Code: q7.py

As mentioned this question is aimed at Machine Learning Engineers so, because I am applying as a data engineer not at me. It did however take me back to some courses I followed on topics like this during my masters so I decided to give it a quick try but no go to full out on it.

Some shortcuts I took were dropping all non categorical columns as coming up with appropriate encoding was for me out of scope. I.E. I think it would have been useful to create a low to high energy consumption category, same as for age or the square meters.
I also didn't spend any time finetuning parameters of models and just went with the defaults.

With these shortcuts in mind I tried finding the most important attributes of a customer that bought a Toon using a Random Forest and a Logistical Regression. I chose these because they are relatively simple to implement and give clear explainability about which attributes are actually relevant.

I also noticed that the dataset wasn't close to equally distributed on the parameter we care about. This lead to the model always predicting that a customer wouldn't be interested and gaining high accuracy this way.

| has_bought_toon | n_customers |
| --------------- | ----------- |
| true            | 411         |
| false           | 19589       |

I think this in combination with the shortcuts I took lead to the fact that I did get results, but they weren't meaningful.

## Question 8: Capture the flag
I quite liked this addition, it reminded me of the CTF events that are hosted within the ethical hacking community.

During the assignemnts I found the following flags:
- Analzying the DNS record: FLAG{2f0056e5-cac9-4ad5-87e9-dfea199f40f6}
- Decoding the Base64 encoded string in the assessment: FLAG{7274e5dc-ab60-4fc2-8f51-ee6eceb6bef7}
- API country response: FLAG{d90ef201-1a5b-495a-ac90-44da0e5c49b1}
- API country header: FLAG{184b6747-6871-49a3-b953-11dd23006097}
- SSH box env variable: FLAG{e8027a95-7031-49ab-b156-4e8828e5a0cc}
- RDBMS sql_function: FLAG{b5c8d8be-419a-4757-8310-f1c7b1cabd5f}
- column_info dataset: FLAG{533db89f-7129-4f2c-96f0-a3fb2b39a436}
- Cat picture flag: FLAG{7d9de71a-675d-4fed-acff-61073f85bebc}

