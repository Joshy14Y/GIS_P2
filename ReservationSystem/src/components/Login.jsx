import Button from 'react-bootstrap/Button';
import FloatingLabel from 'react-bootstrap/FloatingLabel';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import { useEffect, useState } from 'react';

export const Login = () => {

    const [identifier, setIdentifier] = useState(0);


    function handleSubmit(e) {
        // Previene que el navegador recargue la página
        console.log('identifier', identifier);
        e.preventDefault();
        /*
        

        console.log('event:', e);
        // Lee los datos del formulario

        const form = e.target;
        const formData = new FormData(form);
        const formJson = Object.fromEntries(formData.entries());
        console.log(formJson);
        
            // Puedes pasar formData como el cuerpo de la consulta directamente:
            fetch('/some-api', { method: form.method, body: formData });
        
            // O puedes trabajar con él como un objecto plano:
            const formJson = Object.fromEntries(formData.entries());
            console.log(formJson);
        */
    }
    useEffect(() => {
        if (identifier !== 0) console.log('UseEffect identifier', identifier)
    }, [identifier])


    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <Card style={{ width: '20rem', alignItems: 'center' }}>
                <Card.Img variant="top" />
                <Card.Body style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Card.Title>Classroom Reservation System</Card.Title>
                    <form onSubmit={(e) => handleSubmit(e)}>
                        <FloatingLabel
                            controlId="floatingInput"
                            label="Institutional identification"
                            className="m-3"
                        >
                            <Form.Control onChange={(e) => { setIdentifier(e.target.value) }} type="number" placeholder="Type Institutional identification" />
                        </FloatingLabel>
                        <Button type="submit" className="m-3" variant="primary">Login</Button>
                    </form>

                </Card.Body>
            </Card>
        </div>
    )
}
