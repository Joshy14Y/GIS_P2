import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import { formatDate } from '../utils';
import PropTypes from 'prop-types';

export const ReservationConfirmCard = ({ reservation, onAccept, onDecline }) => {

    return (
        <div key={reservation.reservation_id} className="d-flex justify-content-center align-items-center m-5" >
            <Card className="w-50">
                <Card.Header as="h5">Reservacion # {reservation.reservation_id}</Card.Header>
                <Card.Body>
                    <Card.Title>Nombre: {reservation.reservationname}</Card.Title>
                    <Card.Text>
                        Fecha: {formatDate(reservation.date)}
                    </Card.Text>
                    <Card.Text>
                        Hora: {reservation.start_time} hasta {reservation.end_time}
                    </Card.Text>
                    <Card.Text>
                        Lugar: {reservation.classroomname}
                    </Card.Text>
                    <div className="d-flex justify-content-between">
                        <Button onClick={() => onAccept(reservation.reservation_id)} variant="primary">Aceptar</Button>
                        <Button onClick={() => onDecline(reservation.reservation_id)} variant="primary">Rechazar</Button>
                    </div>
                </Card.Body>
            </Card>
        </div>
    )
}
ReservationConfirmCard.propTypes = {
    reservation: PropTypes.object.isRequired,
    onAccept: PropTypes.func.isRequired,
    onDecline: PropTypes.func.isRequired,
}