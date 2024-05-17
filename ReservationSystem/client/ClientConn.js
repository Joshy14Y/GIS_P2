//const axios = require('axios');
import axios from 'axios';
// Define the base URL where your Express server is running
const baseURL = 'http://localhost:3000';

// consultas al backend

// Define a function to fetch parcelas
export async function getUsers() {
  try {
    const response = await axios.get(`${baseURL}/users`);
    return response.data;
  } catch (error) {
    console.error('Error fetching Users:', error.response.data);
    throw error;
  }
}

export async function getUserReservations(tecId) {
  try {
    const response = await axios.get(`${baseURL}/user_reservations?tec_id=${tecId}`);
    console.log(response.data)
    return response.data; // Retorna directamente los datos de la respuesta
  } catch (error) {
    console.error("Error fetching reservations:", error);
    throw error; // Lanza el error para que pueda ser manejado donde se llame a esta función
  }
}



