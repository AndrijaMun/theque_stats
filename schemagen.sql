CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderTime DATETIME NOT NULL,
    CashierID INTEGER,
    OrderTypeID INTEGER,
    PaymentTypeID INTEGER,
    FOREIGN KEY (CashierID) REFERENCES Cashiers(CashierID),
    FOREIGN KEY (OrderTypeID) REFERENCES OrderTypes(OrderTypeID),
    FOREIGN KEY (PaymentTypeID) REFERENCES PaymentTypes(PaymentTypeID)
);

CREATE TABLE Cashiers (
    CashierID INTEGER PRIMARY KEY AUTOINCREMENT,
    CashierName VARCHAR(30),
    CashierSurname VARCHAR(30)
);

CREATE TABLE OrderTypes (
    OrderTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderType VARCHAR(50)
);

CREATE TABLE PaymentTypes (
    PaymentTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    PaymentType VARCHAR(50)
);

CREATE TABLE OrderInfo (
    OrderInfoID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER,
    ItemID INTEGER,
    ItemAmount INTEGER,
    PriceTotal INTEGER
);