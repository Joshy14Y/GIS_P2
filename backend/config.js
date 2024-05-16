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

// Querys ---------------------------------

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

// Querys ---------------------------------


// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
