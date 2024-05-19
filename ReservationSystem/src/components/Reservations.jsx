import { useEffect, useState } from "react"
import { useSelector } from 'react-redux';
import { confirmReservation, declineReservation, getUserReservations, verificationDistance } from "../../client/ClientConn";
import { ReservationConfirmCard } from "./ReservationConfirmCard";

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
    const [toShowFlag, setToShowFlag] = useState(false);

    const get_Teacher_Reservations = async (id) => {
        try {
            const result = await getUserReservations(id);
            console.log(result);
            return result;
        } catch (error) {
            console.error("Error fetching reservations:", error);
        }
    };

    const onAccept = async (id) => {
        console.log('onAccept', id)
        reservations.map(async (reservation) => {
            if (reservation.reservation_id === id) {
                console.log('es el id');
                let response = await confirmReservation(id);
                console.log(response)
            }
        })
        const updatedReservations = reservations.filter(reservation => reservation.reservation_id !== id);
        setReservations(updatedReservations);
    }

    const onDecline = async (id) => {
        reservations.map(async (reservation) => {
            if (reservation.reservation_id === id) {
                console.log('es el id');
                let response = await declineReservation(id);
                console.log(response)
            }
        })
        
        const updatedReservations = reservations.filter(reservation => reservation.reservation_id !== id);
        setReservations(updatedReservations);
    }

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
            }
        }
        fetchData(id);


        // la verificacion de la distancia
    }, [])


    useEffect(() => {
        console.log('reservations', reservations)
    }, [reservations])

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
                })
                setToShowFlag(true);
            }
        }
        fetchData()
    }, [reservationsToCheck])


    return (
        <div>

            {toShowFlag && reservations.map((reservation) => (
                <div key={reservation.reservation_id}>
                    <ReservationConfirmCard reservation={reservation} onAccept={onAccept} onDecline={onDecline} />
                </div>
            ))}

        </div>
    )
}
