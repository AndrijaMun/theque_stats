CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderTime DATETIME NOT NULL,
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
    PriceTotal INTEGER NOT NULL
);