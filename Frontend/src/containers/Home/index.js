import React from 'react'
import Container from 'react-bootstrap/Container';
import FormLogin from '../../components/FormLogin';
import MyNavbar from "../../components/Navbar";
import MyFooter from "../../components/Footer";

let menuNavbar = [
    {
        name: "",
        rute: ""
    }
]

const Home = () =>{
    return (
        <>
            <MyNavbar menuNavbarHome={menuNavbar}/>
            
            <Container style={{marginTop: "80px"}}>
                <h1>Bienvenido a Surveycado</h1>
                <FormLogin/>
            </Container>
            {/* <MyFooter/> */}
        </>
    );
}

export default Home;