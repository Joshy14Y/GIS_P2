import Button from 'react-bootstrap/Button';
import FloatingLabel from 'react-bootstrap/FloatingLabel';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import { useEffect, useState } from 'react';
import { getUsers } from '../../client/ClientConn';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { addId } from '../redux/idSlice';

export const Login = () => {

    //const id = useSelector(state => state.identifier.id);
    const dispatch = useDispatch();

    const [identifier, setIdentifier] = useState(0);
    const [users, setUsers] = useState([]);
    const [userFlag, setUserFlag] = useState(false);
    const navigate = useNavigate();

    function handleSubmit(e) {
        // Previene que el navegador recargue la página
        console.log('identifier', identifier);
        e.preventDefault();

        users.map((user) => {
            if (user.tec_id === identifier) {
                console.log('el usuario existe');
                setUserFlag(true);
            }
        })
    }
    
    const get_Teachers = async () => {
        let data = []
        const result = await getUsers();
        result.map((user) => {
            data.push(user)
        })
        setUsers(data);
    }
    useEffect(() => {
        if (identifier !== 0) console.log('UseEffect identifier', identifier)
    }, [identifier])

    useEffect(() => {
        if (users.length > 0) console.log(users)
    }, [users])

    useEffect(() => {
        async function fetchData() {
            // You can await here
            await get_Teachers();
        }
        fetchData();
    }, [])


    useEffect(() => {

        if (userFlag) {
            console.log(userFlag);
            dispatch(addId(identifier));
            navigate('/reservation', { replace: true });
        }

    }, [userFlag])

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <Card style={{ width: '20rem', alignItems: 'center', backgroundColor: '#27B4C4' }}>
                <Card.Img variant="top" />
                <Card.Body style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Card.Title>Classroom Reservation System</Card.Title>
                    <form style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }} onSubmit={(e) => handleSubmit(e)}>
                        <FloatingLabel
                            controlId="floatingInput"
                            label="Institutional identification"
                            className="m-3"
                        >
                            <Form.Control onChange={(e) => { setIdentifier(e.target.value) }} type="number" placeholder="Type Institutional identification" />
                        </FloatingLabel>
                        <Button type="submit" size="lg" className="m-3" variant="primary">Login</Button>
                    </form>
                </Card.Body>
            </Card>
        </div>
    )
}
