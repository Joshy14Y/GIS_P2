import { useEffect, useState } from "react"
import { useSelector } from 'react-redux';
import { getUserReservations, verificationDistance } from "../../client/ClientConn";

export const Reservations = () => {

    const id = useSelector(state => state.identifier.id);

    const [coordinates, setCoordinates] = useState(
        {
            lat: 0,
            log: 0
        }
    )

    const [reservations, setReservations] = useState([]);
    const [reservationsToCheck, setReservationsToCheck] = useState([]);


    const get_Teacher_Reservations = async (id) => {
        try {
            const result = await getUserReservations(id);
            console.log(result);
            return result;
        } catch (error) {
            console.error("Error fetching reservations:", error);
        }
    };


    useEffect(() => {
        navigator.geolocation.getCurrentPosition((position) => {
            setCoordinates({
                lat: position.coords.latitude,
                log: position.coords.longitude
            })
        })

        async function fetchData(id) {
            if (id !== null) {
                const response = await get_Teacher_Reservations(id)
                setReservationsToCheck(response);
                console.log(response);
            }
        }
        fetchData(id);


        // la verificacion de la distancia
    }, [])


    useEffect(() => {
        console.log('coordinates', coordinates)
    }, [coordinates])

    useEffect(() => {

        async function fetchData() {
            if (reservationsToCheck.length > 0) {
                reservationsToCheck.map(async (reservation) => {
                    const response = await verificationDistance(coordinates.lat, coordinates.log, reservation.geom);
                    if (response === true) {
                        setReservations(prev => [...prev, reservation]);
                    }
                    console.log('response from ckecking function: ', response)
                })
            }
        }
        fetchData()
    }, [reservationsToCheck])


    return (
        <div>
            <p>this is a message</p>
        </div>
    )
}
