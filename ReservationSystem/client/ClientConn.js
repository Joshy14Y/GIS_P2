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

export async function verificationDistance(lat, log, geometry) {
  try {
    const response = await axios.get(`${baseURL}/check_distance?lat=${lat}&log=${log}&geometry=${geometry}`);
    return response.data[0].check_distance; // Retorna directamente los datos de la respuesta
  } catch (error) {
    console.error("Error verification distance:", error);
    throw error; // Lanza el error para que pueda ser manejado donde se llame a esta función
  }
}

export async function confirmReservation(id) {
  try {
    const response = await axios.put(`${baseURL}/update_reservation?id=${id}`);
    return response
  } catch (error) {
    console.error("Error confirming reservation:", error);
    throw error; // Lanza el error para que pueda ser manejado donde se llame a esta función
  }
}

export async function declineReservation(id) {
  try {
    const response = await axios.post(`${baseURL}/delete_reservation?id=${id}`);
    return response
  } catch (error) {
    console.error("Error deleting reservation:", error);
    throw error; // Lanza el error para que pueda ser manejado donde se llame a esta función
  }
}
