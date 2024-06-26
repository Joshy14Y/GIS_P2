require("dotenv").config();

const express = require("express");
const { Pool } = require("pg");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
const port = 3000;

// Configure your PostgreSQL connection
const pool = new Pool({
  user: process.env.USER,
  host: process.env.HOST,
  database: process.env.DATABASE,
  password: process.env.PASSWORD,
  port: process.env.PORT, // Default port 5432 if not specified in .env
});

console.log(pool);

// Enable CORS for all routes
app.use(cors());

// Parse URL-encoded bodies (as sent by HTML forms)
app.use(bodyParser.urlencoded({ extended: false }));

// Parse JSON bodies (as sent by API clients)
app.use(bodyParser.json());

// Define an Express route handler to execute the function
app.get("/users", async (req, res) => {
  try {
    // Connect to the database
    const client = await pool.connect();
    // Execute the function
    const result = await client.query(
      "select * from p2jjl.user"
    );
    // Release the client back to the pool
    client.release();
    // Send the result as JSON response
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching users:", error);
    res.status(500).json({ error: "Internal server error" });
  }
})


app.get("/user_reservations", async (req, res) => {
  const { tec_id } = req.query;

  if (!tec_id) {
    return res.status(400).json({ error: "Missing tec_id parameter" });
  }

  try {
    // Data base connection
    const client = await pool.connect();

    // Query to execute
    const result = await client.query(
      `	   SELECT r.*, 
      c.*, 
      c.name as classroomName,
      r.name as reservationName
      FROM p2jjl.reservation AS r
      INNER JOIN p2jjl.classrooms AS c 
      ON r.classroom_id = c.classroom_id
      WHERE r.user_id = (SELECT u.user_id FROM p2jjl."user" u WHERE u.tec_id = $1) 
      AND r.confirmed = false;`,
      [tec_id]
    );

    const { rows } = result;
    // Release the client back to the pool
    client.release();

    // Send the result as response (JSON).
    res.json(rows);
  } catch (error) {
    console.error("Error fetching user reservations:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// peticion para verificar distancia
app.get("/check_distance", async (req, res) => {
  const { lat, log, geometry } = req.query;

  if (!lat) {
    return res.status(400).json({ error: "Missing lat parameter" });
  }
  if (!log) {
    return res.status(400).json({ error: "Missing log parameter" });
  }
  if (!geometry) {
    return res.status(400).json({ error: "Missing geometry parameter" });
  }

  try {
    // Data base connection
    const client = await pool.connect();

    const result = await client.query(`SELECT p2jjl.check_distance($1,$2,$3)`,
      [lat, log, geometry]);

    const { rows } = result;
    // Release the client back to the pool
    client.release();

    // Send the result as response (JSON).
    res.json(rows);
  } catch (error) {
    console.error("Error verification distance:", error);
    res.status(500).json({ error: "Internal server error" });
  }

});

app.post("/delete_reservation", async (req, res) => {
  const { id } = req.query;
  if (!id) {
    return res.status(400).json({ error: "Missing id parameter" });
  }

  try {
    // Database connection
    const client = await pool.connect();

    const result = await client.query(`DELETE FROM p2jjl.reservation WHERE reservation_id = $1 RETURNING *;`, [id]);

    // Release the client back to the pool
    client.release();

    // If no rows were deleted, the reservation was not found
    if (result.rowCount === 0) {
      return res.status(404).json({ error: "Reservation not found" });
    }

    // Send a success response
    res.status(200).json({ message: "Reservation deleted successfully" });
  } catch (error) {
    console.error("Error deleting reservation:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.put("/update_reservation", async (req, res) => {
  const { id } = req.query;
  if (!id) {
    return res.status(400).json({ error: "Missing id parameter" });
  }

  try {
    // Database connection
    const client = await pool.connect();

    // Perform the update query
    const result = await client.query(`UPDATE p2jjl.reservation SET confirmed = TRUE WHERE reservation_id = $1 RETURNING *;`, [id]);

    // Release the client back to the pool
    client.release();

    // Check if any rows were updated
    if (result.rowCount === 0) {
      return res.status(404).json({ error: "Reservation not found" });
    }

    // Send a success response
    res.status(200).json({ message: "Reservation updated successfully", reservation: result.rows[0] });
  } catch (error) {
    console.error("Error updating reservation:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
