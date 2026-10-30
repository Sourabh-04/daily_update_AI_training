-- C1. Display all parts belonging to the Mechanical category

SELECT *
FROM parts
WHERE category = 'Mechanical';


-- C2. Display parts with unit_price above 1000, ordered from highest price to lowest

SELECT *
FROM parts
WHERE unit_price > 1000
ORDER BY unit_price DESC;


-- C3. Find the average unit_price for each category

SELECT
    category,
    AVG(unit_price) AS average_unit_price
FROM parts
GROUP BY category;


-- C4. Find the total stock quantity for each category

SELECT
    category,
    SUM(stock_qty) AS total_stock_quantity
FROM parts
GROUP BY category;


-- C5. Display every purchase order with supplier_name, order_date and status using a JOIN

SELECT
    s.supplier_name,
    po.order_date,
    po.status
FROM purchase_orders po
JOIN suppliers s
    ON po.supplier_id = s.supplier_id;


-- C5. Display every purchase order with supplier_name, order_date and status using a JOIN.
SELECT
    po.po_id,
    s.supplier_name,
    po.order_date,
    po.status
FROM suppliers s
JOIN purchase_orders po
    ON s.supplier_id = po.supplier_id
JOIN purchase_order_items poi
    ON po.po_id = poi.po_id
JOIN parts p
    ON poi.part_id = p.part_id;


-- C6. Join purchase_orders, purchase_order_items and parts to display po_id, part_name, quantity and
-- unit_price.

SELECT
    po.po_id,
    p.unit_price,
    p.part_name,
    poi.quantity
From purchase_orders po
JOIN purchase_order_items poi
    ON po.po_id = poi.po_id
JOIN parts p
    ON poi.part_id = p.part_id;

-- C7. Extend the previous query to calculate line_total = quantity × unit_price.

SELECT
    po.po_id,
       p.unit_price,
    p.part_name,
    poi.quantity,
	poi.quantity*p.unit_price as line_total
from purchase_orders po
JOIN purchase_order_items poi
    ON po.po_id = poi.po_id
JOIN parts p
    ON poi.part_id = p.part_id;
-- C8. Use a LEFT JOIN to display all suppliers, including suppliers that have never received a purchase order.
SELECT
   
    s.supplier_name,
    po.order_date,
    po.status
FROM suppliers s
left JOIN purchase_orders po
    ON s.supplier_id = po.supplier_id


-- C9. Display only suppliers that have no purchase orders.
SELECT 
    s.supplier_name,
    po.order_date,
    po.status
FROM suppliers s
left JOIN purchase_orders po
    ON s.supplier_id = po.supplier_id
	where po.order_date is Null
-- C10. Create a view named purchase_order_summary showing po_id, supplier_name, part_name, quantity,
--unit_price, line_total and status. Query the view for Pending orders.

create view purchase_order as 
SELECT
    po.po_id,
    s.supplier_name,
    po.order_date,
	p.part_name,
	p.unit_price,
	poi.quantity*p.unit_price as line_total,
	poi.quantity,
    po.status
FROM suppliers s
JOIN purchase_orders po
    ON s.supplier_id = po.supplier_id
JOIN purchase_order_items poi
    ON po.po_id = poi.po_id
JOIN parts p
    ON poi.part_id = p.part_id;

---
-- C11. Create a function calculate_part_discount(amount): if amount >= 2000 return 10% of amount, otherwise
-- return 0. Use it with the parts table.
create or replace function calculate_part_discount(num1 numeric)
Returns float as $$
begin  
if num1 >= 2000 then return num1*0.1 ;
else return num1;
end if;
END;
$$ Language plpgsql;


select calculate_part_discount(unit_price) from parts



-- C12. Create a function final_part_price(amount) that returns amount minus calculate_part_discount(amount).
-- Use it in a SELECT query.

create or replace function final_part_price(num1 numeric)
Returns float as $$
begin  
  return num1 - calculate_part_discount(num1);
END;
$$ Language plpgsql;

select unit_price ,calculate_part_discount(unit_price),final_part_price(unit_price) from parts

-- C13. Create a stored procedure with parameters named update_po_status that accepts po_id and new_status
-- and updates the matching purchase order. Call it once and verify the result.

create or replace procedure update_po_status(
p_po_id INT,
p_new_status varchar(30)
)
Language plpgsql as $$
Begin 
UPdate purchase_orders
set status = p_new_status
where po_id = p_po_id;

end;
$$;

call update_po_status(1002,'received')

select * from purchase_orders

-- C14. Create a stored procedure without parameters named mark_old_pending_orders that changes Pending
-- orders dated before 2026-10-04 to Received. Run it and verify the results.
create or replace procedure mark_old_pending_orders(
)
Language plpgsql as $$
Begin 
UPdate purchase_orders
set status = 'Received'
where order_date < '2026-10-04' and status = 'Pending' ;

end;
$$;
call mark_old_pending_orders()

-- C15. Normalization question: Suppose supplier_name, supplier_city, part_name, part_category, po_id and
-- quantity were all stored repeatedly in one large table. Identify at least two repeated facts and suggest how you
-- would separate the data into tables.

--- ANS - (Supplier, supplier_city) and Part_information(part_name,part_category) woould repaet whnerver there 
--is purchase order and same part puchase in multiple purchase orders.
---To normalise : Store supllier details in supplier table and refeence it with supplier id.
				-- : add part detials in part table and refrence it part_id
				-- : store purchase orders in purchase_orders and order line items in puchase order itms .





	