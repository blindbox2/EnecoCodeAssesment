WITH
	customer_invoice_invoice_lines
	AS
	(
		SELECT
			customer.customer_id,
			inv_line.track_id,
			inv_line.quantity * inv_line.unit_price AS gross_revenue
		FROM invoice_line inv_line
			INNER JOIN invoice
			ON inv_line.invoice_id = invoice.invoice_id
			INNER JOIN customer
			ON invoice.customer_id = customer.customer_id
	),
	distinct_jazz_customers
	AS
	(
		SELECT DISTINCT
			ciil.customer_id,
			genre.name AS customer_type
		FROM customer_invoice_invoice_lines ciil
			INNER JOIN track track
			ON ciil.track_id = track.track_id
			INNER JOIN genre
			ON track.genre_id  = genre.genre_id
		where genre.name = 'Jazz'
	),
	total_revenue_per_customer
	AS
	(
		SELECT
			ciil.customer_id,
			SUM(ciil.gross_revenue) AS sum_gross_revenue
		FROM customer_invoice_invoice_lines AS ciil
		GROUP BY ciil.customer_id
	)
SELECT
	COALESCE(jazz_cus.customer_type, 'Not Jazz') AS customer_type,
	AVG(trpc.sum_gross_revenue) AS average_gross_revenue
FROM total_revenue_per_customer trpc
	LEFT JOIN DISTINCT_jazz_customers AS jazz_cus
	ON trpc.customer_id = jazz_cus.customer_id
GROUP BY customer_type;