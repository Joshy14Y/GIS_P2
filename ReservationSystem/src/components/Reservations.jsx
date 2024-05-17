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
            console.log(position.coords)
            setCoordinates({
                lat: position.coords.latitude,
                log: position.coords.longitude
            })
        })

    }, [])

    useEffect(() => {
        console.log('coordinates', coordinates)
    }, [coordinates])


    useEffect(() => {
        console.log('id', id)
        if (id !== null) {
            get_Teacher_Reservations(id);
        }

    }, [])

    return (
        <div>
            <p>this is a message</p>
        </div>
    )
}
