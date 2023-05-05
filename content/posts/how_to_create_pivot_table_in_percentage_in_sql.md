---
author: "CJ Hsu"
title: "How to Create Pivot Table in Percentage in SQL"
date: "2023-05-05"
summary: "This article provides code examples for generating pivot tables with PostgreSQL."
description: "This article explores how to generate pivot tables with PostgreSQL using sample transaction data and provides two possible ways to represent the percentage of transactions for each person at each date."
categories: ["Tech", "Data"]
tags: ["How-to", "SQL", "PostgreSQL", "conditional aggregation"]
---

Suppose there is a table named "transaction" in a PostgreSQL database. Each row contains four pieces of information: the name of the person making the transaction, the type of transaction, the amount of the transaction, and the date on which the transaction occurred. You want to generate a pivot table that shows the percentage of transactions for each person at each date within a specified date range. The rows of the table should represent the people, and the columns should represent the dates.

Below is the data that we will be using in this example. 

| name | type        | amount | transaction date |
|------|-------------|--------|------------------|
| Jack | cash out    | 30.00  | 2023-05-01       |
| Jack | credit card | 75.25  | 2023-05-01       |
| Jack | cash out    | 20.00  | 2023-05-02       |
| Jack | cash in     | 150.00 | 2023-05-03       |
| Jack | credit card | 40.89  | 2023-05-03       |
| Lucy | cash in     | 100.00 | 2023-05-01       |
| Lucy | credit card | 85.43  | 2023-05-01       |
| Lucy | cash in     | 250.00 | 2023-05-02       |
| Lucy | credit card | 45.67  | 2023-05-02       |
| Lucy | cash out    | 15.00  | 2023-05-03       |

The desired output is as follows, with values represented as percentages:

| name  | may_01 | may_02 | may_03 |
|-------|--------|--------|--------|
| Jack  | 40     | 20     | 40     |
| Lucy  | 40     | 40     | 20     |

You may have already written something like this:

```sql

select name
	,sum(case transaction_date when '2023-05-01' then 1 else 0 end) as may_01
	,sum(case transaction_date when '2023-05-02' then 1 else 0 end) as may_02
	,sum(case transaction_date when '2023-05-03' then 1 else 0 end) as may_03
from transaction
group by name
order by name
;

```

which generates a table with rows representing individuals and columns representing dates, but the numbers in the table represent counts, not percentages. To calculate percentages, you will need to divide the count by the population. There are two possible ways to do this - one using a common table expression and one without.

Personally, I prefer using a common table expression because it helps me understand the calculation process, but this option results in a longer code. For those who prefer more concise code, the option without a common table expression will be a better fit.

The main difference between the two codes provided is how they handle null values. The code that uses a common table expression will count transactions without transaction dates for an individual, while the code without a common table expression will skip them.

Both codes are provided below.

**With common table expression**

```sql

with name_count as (
	select name
		,count(*) as name_count
	from transaction
	group by name
),
name_date_percentage as (
	select a.name
		,a.transaction_date
		,(count(a.*) * 100 / b.name_count) as name_date_percentage
	from transaction a
	inner join name_count b
	on a.name = b.name
	group by a.name, a.transaction_date, b.name_count
)
select name
	,max(case transaction_date when '2023-05-01' then name_date_percentage else 0 end) as may_01
	,max(case transaction_date when '2023-05-02' then name_date_percentage else 0 end) as may_02
	,max(case transaction_date when '2023-05-03' then name_date_percentage else 0 end) as may_03
from name_date_percentage
group by name
order by name
;

```

**Without common table expression**

```sql

select name
	,sum(case transaction_date when '2023-05-01' then 1 else 0 end) * 100 / sum(case when transaction_date between '2023-05-01' and '2023-05-03' then 1 else 0 end) as may_01
	,sum(case transaction_date when '2023-05-02' then 1 else 0 end) * 100 / sum(case when transaction_date between '2023-05-01' and '2023-05-03' then 1 else 0 end) as may_02
	,sum(case transaction_date when '2023-05-03' then 1 else 0 end) * 100 / sum(case when transaction_date between '2023-05-01' and '2023-05-03' then 1 else 0 end) as may_03
from transaction
group by name
order by name
;

```

To try it out for yourself, use the following code to set up the environment.

```sql

CREATE TABLE IF NOT EXISTS transaction
(
    name character varying(255),
    type character varying(255),
    amount numeric(10,2),
    transaction_date date
);

INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Jack', 'cash out', 30.00, '2023-05-01');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Jack', 'credit card', 75.25, '2023-05-01');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Jack', 'cash out', 20.00, '2023-05-02');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Jack', 'cash in', 150.00, '2023-05-03');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Jack', 'credit card', 40.89, '2023-05-03');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Lucy', 'cash in', 100.00, '2023-05-01');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Lucy', 'credit card', 85.43, '2023-05-01');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Lucy', 'cash in', 250.00, '2023-05-02');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Lucy', 'credit card', 45.67, '2023-05-02');
INSERT INTO transaction (name, type, amount, transaction_date) VALUES ('Lucy', 'cash out', 15.00, '2023-05-03');

```