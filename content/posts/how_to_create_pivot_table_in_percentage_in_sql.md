---
author: "CJ Hsu"
title: "How to Create Pivot Table in Percenrage in SQL"
date: "2023-05-05"
summary: "This article provides code examples for generating pivot tables with PostgreSQL."
description: "This article explores how to generate pivot tables with PostgreSQL using sample transaction data and provides two possible ways to represent the percentage of transactions for each person at each date."
categories: ["Tech"]
tags: ["How-to", "SQL", "PostgreSQL", "conditional aggregation"]
---

Suppose there is a table named "transaction" in a PostgreSQL database. Each row contains four pieces of information: the name of the person making the transaction, the type of transaction, the amount of the transaction, and the date on which the transaction occurred. You want to generate a pivot table that shows the percentage of transactions for each person at each date within a specified date range. The rows of the table should represent the people, and the columns should represent the dates.

Below is an example of the data that we will be using. 

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

You want output format to be as follows, with values represented as percentages:

|       | may_01 | may_02 | may_03 |
|-------|--------|--------|--------|
| Jack  | 40     | 20     | 40     |
| Lucy  | 40     | 40     | 20     |

You may have written something like this:

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

which generates a table with rows representing people and columns representing dates, but the values are in count rather than percentages. To convert the values to percentages, there are two possible ways to write the code: one with a common table expression and one without. Personally, I prefer the version with the common table expression because it allows for easy adjustment of the denominator if needed. However, when the "transaction_date" field contains null values, extra care is necessary. In this example, the version without the common table expression seems to be a better fit. You can find both codes below.

**Use common table expression**

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

**No common table expression**

```sql

select name
	,sum(case transaction_date when '2023-05-01' then 1 else 0 end) * 100 / sum(case when transaction_date is not null then 1 else 0 end) as may_01
	,sum(case transaction_date when '2023-05-02' then 1 else 0 end) * 100 / sum(case when transaction_date is not null then 1 else 0 end) as may_02
	,sum(case transaction_date when '2023-05-03' then 1 else 0 end) * 100 / sum(case when transaction_date is not null then 1 else 0 end) as may_03
from transaction
group by name
order by name
;

```

To reproduce the environment on your own, use the code below to create the table.

```sql

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