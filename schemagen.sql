CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderTime DATETIME NOT NULL,
    OrderAmount DECIMAL(5,2) GENERATED ALWAYS AS (SUM(SELECT PriceTotal FROM OrderInfo WHERE OrderInfo.OrderID = OrderID)),
    CashierID INTEGER NOT NULL,
    OrderTypeID INTEGER NOT NULL,
    PaymentTypeID INTEGER NOT NULL,
    FOREIGN KEY (CashierID) REFERENCES Cashiers(CashierID),
    FOREIGN KEY (OrderTypeID) REFERENCES OrderTypes(OrderTypeID),
    FOREIGN KEY (PaymentTypeID) REFERENCES PaymentTypes(PaymentTypeID)
);

CREATE TABLE Cashiers (
    CashierID INTEGER PRIMARY KEY AUTOINCREMENT,
    CashierName VARCHAR(30) NOT NULL,
    CashierSurname VARCHAR(30) NOT NULL
);

CREATE TABLE OrderTypes (
    OrderTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderType VARCHAR(50) NOT NULL
);

CREATE TABLE PaymentTypes (
    PaymentTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    PaymentType VARCHAR(50) NOT NULL
);

CREATE TABLE OrderInfo (
    OrderInfoID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER NOT NULL,
    ItemID INTEGER NOT NULL,
    ItemAmount INTEGER NOT NULL,
    PriceTotal DECIMAL(5, 2) GENERATED ALWAYS AS (ItemAmount * (SELECT ItemPrice FROM Items WHERE Items.ItemID = ItemID)),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID)
);

CREATE TABLE Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemName VARCHAR(50) NOT NULL,
    ItemTypeID INTEGER,
    ItemPrice DECIMAL(4, 2) NOT NULL,
    FOREIGN KEY ItemTypeID REFERENCES ItemTypes(ItemTypeID)
);

CREATE TABLE ItemTypes (
    ItemTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemTypeName VARCHAR(50) NOT NULL
);