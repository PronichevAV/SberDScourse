/* Выберите заказчиков из Германии, Франции и Мадрида, выведите их название, страну и адрес */

SELECT CustomerName, Country, Address
FROM Customers
WHERE Country = 'Germany'
   or Country = 'France'
   or City = 'Madrid';

/* Выберите топ 3 страны по количеству заказчиков, выведите их названия и количество записей */
SELECT Country, COUNT(CustomerName) AS Count
FROM Customers
GROUP BY Country
ORDER BY Count DESC
    LIMIT 3;

/* Выберите перевозчика, который отправил 10-й по времени заказ, выведите его название, и дату отправления */
SELECT ShipperName, OrderDate
FROM Orders
         JOIN Shippers ON Orders.ShipperID = Shippers.ShipperID
ORDER BY OrderDate LIMIT 1
OFFSET 9;

/* Выберите самый дорогой заказ, выведите список товаров с их ценами */
SELECT ProductName, Price
FROM OrderDetails
         JOIN Products ON OrderDetails.ProductID = Products.ProductID
WHERE OrderID =
      (
          SELECT OrderID
          FROM OrderDetails
                   JOIN Products ON OrderDetails.ProductID = Products.ProductID
          GROUP BY OrderID
          ORDER BY SUM(Quantity * Price) DESC
    LIMIT 1
    )

/* Какой товар больше всего заказывали по количеству единиц товара, выведите его название и количество единиц в каждом из заказов */
SELECT OrderID, ProductName, Quantity
FROM OrderDetails
         JOIN Products ON OrderDetails.ProductID = Products.ProductID
WHERE OrderDetails.ProductID =
      (
          SELECT ProductID
          FROM OrderDetails
          GROUP BY ProductID
          ORDER BY SUM(Quantity) DESC
    LIMIT 1
    )

/* Выведите топ 5 поставщиков по количеству заказов, выведите их названия, страну, контактное лицо и телефон */
SELECT SupplierName, Country, Phone
FROM OrderDetails
    JOIN Products
ON OrderDetails.ProductID = Products.ProductID
    JOIN Suppliers ON Suppliers.SupplierID = Products.SupplierID
GROUP BY SupplierName
ORDER BY COUNT (OrderID) DESC
    LIMIT 5

/* Какую категорию товаров заказывали больше всего по стоимости в Бразилии, выведите страну, название категории и сумму */
SELECT CategoryName, Country, SUM(Price * Quantity) AS Sum
FROM OrderDetails
    JOIN Orders
ON OrderDetails.OrderID = Orders.OrderID
    JOIN Customers ON Orders.CustomerID = Customers.CustomerID
    JOIN Products ON OrderDetails.ProductID = Products.ProductID
    JOIN Categories ON Products.CategoryID = Categories.CategoryID
WHERE Customers.Country = 'Brazil'
GROUP BY Categories.CategoryID
ORDER BY SUM (Price * Quantity) DESC
    LIMIT 1

/* Какая разница в стоимости между самым дорогим и самым дешевым заказом из США */
SELECT Country, MAX(Price * Quantity) - MIN(Price * Quantity) AS Diff
FROM OrderDetails
         JOIN Orders ON OrderDetails.OrderID = Orders.OrderID
         JOIN Customers ON Orders.CustomerID = Customers.CustomerID
         JOIN Products ON OrderDetails.ProductID = Products.ProductID
WHERE Customers.Country = 'USA'

/* Выведите количество заказов у каждого их трех самых молодых сотрудников, а также имя и фамилию во второй колонке */
SELECT Employees.FirstName || ' ' || Employees.LastName AS EmployeeName, COUNT(OrderID) AS OrdersCount
FROM Orders
         JOIN Employees ON Employees.EmployeeID = Orders.EmployeeID
GROUP BY Orders.EmployeeID
ORDER BY Employees.BirthDate DESC
LIMIT 3

/* Сколько банок крабового мяса всего было заказано */
SELECT SUM(Quantity) * (SELECT CAST(SUBSTR(Unit, 6, 1) AS INTEGER)
                        FROM Products
                        WHERE ProductName = 'Boston Crab Meat') AS TotalBostonCrabMeatTinsSold
FROM OrderDetails
         JOIN Products ON OrderDetails.ProductID = Products.ProductID
WHERE ProductName = 'Boston Crab Meat'