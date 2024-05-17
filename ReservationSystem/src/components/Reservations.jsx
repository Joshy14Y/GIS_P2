import { useEffect, useState } from "react"
import { useSelector } from 'react-redux';
import { getUserReservations } from "../../client/ClientConn";

export const Reservations = () => {

    const id = useSelector(state => state.identifier.id);

    const [coordinates, setCoordinates] = useState(
        {
            lat: 0,
            log: 0
        }
    )

    const get_Teacher_Reservations = async (id) => {
        try {
            const result = await getUserReservations(id);
            console.log(result);
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
        if (id !== null) {
            get_Teacher_Reservations(id);
        }

    }, [])

    useEffect(() => {
        console.log('coordinates', coordinates)
    }, [coordinates])


    return (
        <div>
            <p>this is a message</p>
        </div>
    )
}
