-- main table for all orders
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderTime DATETIME,
    OrderAmount DECIMAL(5,2),
    StampCouponAmount INTEGER,
    CashierID INTEGER,
    OrderTypeID INTEGER,
    PaymentTypeID INTEGER,
    FOREIGN KEY (CashierID) REFERENCES Cashiers(CashierID),
    FOREIGN KEY (OrderTypeID) REFERENCES OrderTypes(OrderTypeID),
    FOREIGN KEY (PaymentTypeID) REFERENCES PaymentTypes(PaymentTypeID)
);


-- table for all cashiers that serve orders
CREATE TABLE Cashiers (
    CashierID INTEGER PRIMARY KEY AUTOINCREMENT,
    CashierName VARCHAR(30) NOT NULL,
    CashierSurname VARCHAR(30) NOT NULL
);

-- table for ordering methods
CREATE TABLE OrderTypes (
    OrderTypeID INTEGER PRIMARY KEY,
    OrderType VARCHAR(50) NOT NULL
);

-- table for payment methods
CREATE TABLE PaymentTypes (
    PaymentTypeID INTEGER PRIMARY KEY,
    PaymentType VARCHAR(50) NOT NULL
);

-- table for each item in an order 
CREATE TABLE OrderInfo (
    OrderInfoID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER NOT NULL,
    ItemID INTEGER NOT NULL,
    -- same items are grouped together
    ItemAmount INTEGER NOT NULL,
    PriceTotal DECIMAL(5, 2),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID)
);

-- table for items on the menu
CREATE TABLE Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemName VARCHAR(100) NOT NULL,
    ItemTypeID INTEGER,
    ItemFlavourID INTEGER,
    ItemPrice DECIMAL(4, 2) NOT NULL,
    FOREIGN KEY (ItemTypeID) REFERENCES ItemTypes(ItemTypeID),
    FOREIGN KEY (ItemFlavourID) REFERENCES ItemFlavours(ItemFlavourID)
);

-- table for item categories
CREATE TABLE ItemTypes (
    ItemTypeID INTEGER PRIMARY KEY,
    ItemTypeName VARCHAR(50) NOT NULL
);

-- table for flavours that span multiple items
CREATE TABLE ItemFlavours (
    ItemFlavourID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemFlavour VARCHAR(50) NOT NULL
);

-- table for extra add-ons on the menu
CREATE TABLE AddOns (
    AddOnID INTEGER PRIMARY KEY AUTOINCREMENT,
    AddOn VARCHAR(50) NOT NULL,
    AddOnTypeID INTEGER,
    AddOnPrice DECIMAL (4,2) NOT NULL,
    FOREIGN KEY (AddOnTypeID) REFERENCES AddOnTypes(AddOnTypeID)
);

-- table for add-on categories
CREATE TABLE AddOnTypes (
    AddOnTypeID INTEGER PRIMARY KEY,
    AddOnType VARCHAR(50) NOT NULL
)

-- table for add-ons paired with an item in an order
CREATE TABLE ItemAddOns (
    ItemAddOnID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderInfoID INTEGER NOT NULL,
    AddOnID INTEGER NOT NULL,
    AddOnAmount INTEGER NOT NULL,
    PriceTotal DECIMAL (5,2),
    FOREIGN KEY (OrderInfoID) REFERENCES OrderInfo(OrderInfoID),
    FOREIGN KEY (AddOnID) REFERENCES AddOns(AddOnID)
);

-- base data entry
INSERT INTO Cashiers VALUES (1, "John", "Doe"), (2, "Mary", "Sue");
INSERT INTO OrderTypes VALUES (1, 'In person'), (2, 'Call in pickup'), (3, 'Wolt delivery'), (4, 'Wolt pickup');
INSERT INTO PaymentTypes VALUES (1, 'Cash'), (2, 'Card'), (3, 'Coupon');
INSERT INTO ItemTypes VALUES (1, 'Tayiaki'), (2, 'Mochi'), (3, 'Ice Cream Cup'), (4, 'Pancake'), (5, 'Beverage'), (6, 'Soft drink');
INSERT INTO ItemFlavours (ItemFlavour) VALUES ('Vanilla'), ('Chocolate'), ('Matcha'), ('Mango'), ('Oreo'), ('Plasma'), ('Bueno'), ('Raffaello'), ('Plain'), ('Peach'), ('Apple'), ('Orange');
INSERT INTO AddOnTypes VALUES (1, 'Liquid Topping'), (2, 'Sprinkle'), (3, 'Cookie'), (4, 'Fruit'), (5, 'Molded Chocolate'), (6, 'Milk Substitution');

INSERT INTO Items (ItemName, ItemTypeID, ItemFlavourID, ItemPrice) VALUES
('Simple Tayiaki', 1, 1, 4),
('Simple Tayiaki', 1, 2, 4),
('Simple Tayiaki', 1, 3, 4.3),
('Simple Tayiaki', 1, 4, 4.3),
('Extra Tayiaki', 1, 5, 5),
('Extra Tayiaki', 1, 6, 5),
('Premium Tayiaki', 1, 7, 6),
('Premium Tayiaki', 1, 8, 6),

('Classic Mochi', 2, 1, 4),
('Classic Mochi', 2, 2, 4),
('Classic Mochi', 2, 3, 4.5),
('Classic Mochi', 2, 4, 4.5),
('Premium Mochi', 2, 1, 5),
('Premium Mochi', 2, 2, 5),
('Premium Mochi', 2, 3, 5.5),
('Premium Mochi', 2, 4, 5.5),

('Standard Ice Cream Cup', 3, 1, 2.8),
('Standard Ice Cream Cup', 3, 2, 2.8),
('Standard Ice Cream Cup', 3, 3, 3.3),
('Standard Ice Cream Cup', 3, 4, 3.3),
('Large Ice Cream Cup', 3, 1, 3.8),
('Large Ice Cream Cup', 3, 2, 3.8),
('Large Ice Cream Cup', 3, 3, 4.3),
('Large Ice Cream Cup', 3, 4, 4.3),

('Cocoa Base Pancake', 4, 9, 3),
('Cocoa Base Pancake', 4, 5, 4),
('Cocoa Base Pancake', 4, 6, 4),
('Cocoa Base Pancake', 4, 7, 5),
('Cocoa Base Pancake', 4, 8, 5),

('Espresso', 5, NULL, 1.3),
('Double Espresso', 5, NULL, 2.1),
('Small Macchiato', 5, NULL, 1.5),
('Standard Macchiato', 5, NULL, 1.8),
('Cappuccino', 5, NULL, 1.8),
('Cafe Latte', 5, NULL, 2),
('Standard Matcha Latte', 5, NULL, 3),
('Large Matcha Latte', 5, NULL, 3.5),
('Affogato', 5, 1, 3),

('Still Water', 6, NULL, 2.5),
('Sparkling Water', 6, NULL, 2.5),
('Coca-Cola', 6, NULL, 2.5),
('Coca-Cola Zero', 6, NULL, 2.5),
('Jana Ice Tea', 6, 10, 2.5),
('Cappy Juice', 6, 11, 2.5),
('Cappy Juice', 6, 12, 2.5);

INSERT INTO AddOns (AddOn, AddOnTypeID, AddOnPrice) VALUES
('Nutella', 1, 0.7),
('White Linolada', 1, 0.7),
('Hazelnut', 1, 0.7),
('Chocolate', 1, 0.7),
('Strawberry', 1, 0.7),
('Forest Fruits', 1, 0.7),
('Caramel', 1, 0.7),

('Oreo', 2, 0.7),
('Plasma', 2, 0.7),
('Coconut', 2, 0.7),

('Oreo', 3, 0.7),
('Plasma', 3, 0.7),

('Blueberry', 4, 0.7),
('Raspberry', 4, 0.7),
('Banana', 4, 0.7),

('Hello Kitty', 5, 0.7),
('Micky Mouse', 5, 0.7),
('Unicorn Ears', 5, 0.7),

('Oat Milk', 6, 0.7),
('Soy Milk', 6, 0.7),
('Lactose Free Milk', 6, 0.7),
('Whipped Cream', NULL, 0.7),

('Tayiaki Twist', NULL, 1);






















