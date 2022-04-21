--task1  (lesson2)
-- oracle: https://leetcode.com/problems/department-top-three-salaries/

WITH agg AS (
    SELECT DepartmentId, Name, Salary, DENSE_RANK()
                                       OVER (PARTITION BY DepartmentId ORDER BY Salary DESC) AS rank
    FROM Employee)
SELECT Department.Name AS "Department", agg.Name AS "Employee", agg.Salary AS "Salary"
FROM agg JOIN Department ON agg.DepartmentId = Department.Id
WHERE agg.rank < 4;

--task2  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/17

SELECT fm.member_name, fm.status, SUM(p.amount*p.unit_price) AS costs
FROM FamilyMembers AS fm JOIN Payments AS p ON p.family_member = fm.member_id
WHERE YEAR(p.date) = 2005
GROUP BY fm.member_id;

--task3  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/13

SELECT name
FROM Passenger
GROUP BY name
HAVING count(name) > 1;

--task4  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/38

SELECT COUNT(first_name) AS count
FROM Student
WHERE first_name = 'Anna';

--task5  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/35

SELECT COUNT(classroom) AS count
FROM Schedule
WHERE YEAR(date) = 2019 AND MONTH(date) = 9 AND DAY(date) = 2;


--task6  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/38

SELECT COUNT(first_name) AS count
FROM Student
WHERE first_name = 'Anna';

--task7  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/32

SELECT FLOOR(AVG(2021 - YEAR(birthday))) AS age
FROM FamilyMembers;

--task8  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/27

SELECT good_type_name, SUM(amount*unit_price) AS costs
FROM Payments
         JOIN Goods ON good=good_id
         JOIN GoodTypes ON type=good_type_id
WHERE YEAR(date) = 2005
GROUP BY good_type_name;

--task9  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/37

SELECT 2021 - MAX(YEAR(birthday)) AS year
FROM Student;

--task10  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/44

SELECT YEAR(CURRENT_DATE) - MIN(YEAR(birthday)) AS max_year
FROM Student
         JOIN Student_in_class ON Student.id=Student_in_class.student
         JOIN Class ON Student_in_class.class=Class.id
WHERE Class.name LIKE '10%';

--task11 (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/20

SELECT status, member_name, SUM(amount * unit_price) AS costs
FROM Payments
         JOIN FamilyMembers ON Payments.family_member=FamilyMembers.member_id
         JOIN Goods ON Goods.good_id=Payments.good
         JOIN GoodTypes ON GoodTypes.good_type_id=Goods.type
WHERE GoodTypes.good_type_name = 'entertainment'
GROUP BY status, member_name;

--task12  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/55

DELETE FROM Company
WHERE Company.id IN (
    SELECT company
    FROM Trip
    GROUP BY company
    HAVING COUNT(id) = (
        SELECT MIN(count)
        FROM (
                 SELECT COUNT(id) AS count
                 FROM Trip
                 GROUP BY company) AS min_count));

--task13  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/45

SELECT classroom
FROM Schedule
GROUP BY classroom
HAVING COUNT(classroom) = (
    SELECT COUNT(classroom)
    FROM Schedule
    GROUP BY classroom
    ORDER BY COUNT(classroom) DESC
    LIMIT 1
);

--task14  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/43

SELECT last_name
FROM Schedule
         JOIN Teacher ON Schedule.teacher=Teacher.id
         JOIN Subject ON Schedule.subject=Subject.id
WHERE name='Physical Culture'
ORDER BY last_name ASC

--task15  (lesson2)
-- https://sql-academy.org/ru/trainer/tasks/63

SELECT CONCAT(last_name, '.', LEFT(first_name, 1), '.', LEFT(middle_name, 1), '.') AS name
FROM Student
ORDER BY last_name, first_name;