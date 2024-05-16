import { Route, Routes } from 'react-router-dom';
import { Login } from './components/Login';
import { Reservations } from './components/Reservations';

function App() {

    return (
        <>
            <Routes>
                <Route path='/' element={<Login />} />
                <Route path='/reservation' element={<Reservations />} />
            </Routes>
        </>
    )
}

export default App