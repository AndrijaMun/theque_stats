CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderTime DATETIME NOT NULL,
    OrderAmount DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN PaymentTypeID = 3 THEN 0
            ELSE SUM(SELECT PriceTotal FROM OrderInfo WHERE OrderInfo.OrderID = OrderID)
        END
        ),
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
    OrderTypeID INTEGER PRIMARY KEY,
    OrderType VARCHAR(50) NOT NULL
);

CREATE TABLE PaymentTypes (
    PaymentTypeID INTEGER PRIMARY KEY,
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
    ItemFlavourID INTEGER,
    ItemPrice DECIMAL(4, 2) NOT NULL,
    FOREIGN KEY ItemTypeID REFERENCES ItemTypes(ItemTypeID),
    FOREIGN KEY ItemFlavourID REFERENCES ItemFlavours(ItemFlavourID)
);

CREATE TABLE ItemTypes (
    ItemTypeID INTEGER PRIMARY KEY,
    ItemTypeName VARCHAR(50) NOT NULL
);

CREATE TABLE ItemFlavours (
    ItemFlavourID INTEGER PRIMARY KEY,
    ItemFlavour VARCHAR(50) NOT NULL
);

INSERT INTO OrderTypes VALUES (1, 'In person'), (2, 'Call in pickup'), (3, 'Wolt delivery'), (4, 'Wolt pickup');
INSERT INTO PaymentTypes VALUES (1, 'Cash'), (2, 'Card'), (3, 'Coupon');
INSERT INTO ItemTypes VALUES (1, 'Tayiaki'), (2, 'Mochi'), (3, 'Ice Cream Cup'), (4, 'Pancake'), (5, 'Coffee / Matcha'), (6, 'Soft drink'), (7, 'Add-on');

