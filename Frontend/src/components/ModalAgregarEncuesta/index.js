import React, {useState, useEffect} from "react";
import { useParams} from 'react-router-dom'
import {Modal, Button, InputGroup, Form} from 'react-bootstrap'
import CardPregunta from '../../components/CardPregunta';
import swal from 'sweetalert';
import axios from 'axios';

// id_encuesta, titulo_encuesta, descripcion_encuesta, id_pregunta, enunciado_pregunta, id_alternativa, enunciado_alternativa, contador_alternativa

//se puede enviar a la base de datos titulos y descripcion sin preguntas

const ModalAgregarEncuesta = () => {

  const idEditor = useParams();
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const [cardList, setCardList] = useState([]);
  const [id_pregunta, setId_Pregunta] = useState(1);
  const [inputs, setInputs] = useState({});
  const [tags, setTags] = useState([]);

  const onAddCardClick = () => {
    if(cardList.length < 10){
      setId_Pregunta(id_pregunta+1);
      setCardList(cardList.concat(<CardPregunta id_pregunta={id_pregunta} handleChange={handleChange}/>));
    }
    else{
      swal("Alto!", "No puedes añadir más preguntas, eso va contra la ley", "error")
    }
  }
  useEffect(() => {
      //DEVELOPMENT URL
      //axios.get(`http://localhost:5000/getTags`).then(response => {
      //DEPLOYMENT URL
      axios.get(`http://152.74.52.191:5009/getTags`).then(response => {
            setTags(response.data)
            console.log(response.data)
        }).catch(err => console.log(err))
    }, [])

  const etiquetas = tags.map(tagcito => {
    const nombre = tagcito.tag
    return(
      <option value={nombre}> {nombre} </option>);
  })

  const vaciarCardListGuardar = (event) => {
    //console.log("length",cardList.length);
    for(let[key,value] in inputs){
      if(value.length===0){
        //console.log("primer if");
        event.preventDefault();
        return false;
      }
    }
    setCardList([]);
    setShow(false);
    setId_Pregunta(1);
/*
    if((cardList.length === 0) || (inputs.titulo_encuesta.length===0) || (inputs.descripcion_encuesta.length===0) || (inputs.enunciado_alternativa.length===0) || (inputs.enunciado_pregunta.length===0)){
      console.log("primer if");
      //event.preventDefault();
    }
    else{
      console.log("EN EL ELSE");
      setCardList([]);
      setShow(false);
      setId_Pregunta(1);
    }
  */
    return true;
  }

  const vaciarCardListCancelar = () => {
    setCardList([]);
    setShow(false);
    setId_Pregunta(1);
  }

  const handleChange = (event) =>{
    const name = event.target.name;
    const value = event.target.value;
    setInputs(values => ({...values, [name]: value}))
    console.log(name,value);
  }

  const handleSubmit = (event) => {
    // const form = event.currentTarget;
    
    // if (form.checkValidity() === false) {
    //   // e.preventDefault();
    //   event.stopPropagation();        
    // }

    // setValidated(true);
    if(!vaciarCardListGuardar())
      return

    //console.log(inputs)
    var dict = []
    var dictP = []
    var dictA = []
    var iterP=1
    var iterA=1;
    dict.push({idEditor: idEditor.idEd})
    for(let [key,value] of Object.entries(inputs)){
      if(key === 'titulo_encuesta'){
        dict.push({
          titulo_encuesta: value
        });
      }
      if(key === 'descripcion_encuesta'){
        dict.push({
          descripcion_encuesta: value
        });
      }
      if(key === 'tag_encuesta'){
        dict.push({
          tag_encuesta: value
        });
      }
      if(key === `pregunta ${iterP}`){
        for(let [keyA,valueA] of Object.entries(inputs)){
          if(keyA === `alternativa ${iterA}_${iterP}`){
            dictA.push({
              enunciado_alternativa: valueA
            });
            iterA++;
          }
        }
        dictP.push({
          enunciado_pregunta: value,
          alternativas: dictA
        });
        dictA = [];
        iterP++;
      }
      iterA=1;
    }
    dict.push({
      preguntas: dictP
    });
    //console.log(dict)

    //console.log(inputs.titulo_encuesta)
    for(let[key,value] in inputs){
      if(value.length===0){
        //console.log("primer if");
        event.preventDefault();
      }
    }
    //DEVELOPMENT POST
    //axios.post('http://localhost:5000/saveEncuesta', {dict} )
    //DEPLOYMENT POST
    axios.post('http://152.74.52.191:5009/saveEncuesta', {dict} )
       .then(res => {
         //console.log(res);
         swal("Correcto!",'Encuesta guardada satisfactoriamente','success')
       })
     //handleClose(true);
    /*
    if((cardList.length === 0) || (inputs.titulo_encuesta.length===0) || (inputs.descripcion_encuesta.length===0) || (inputs.enunciado_alternativa.length===0) || (inputs.enunciado_pregunta.length===0)){
      console.log("primer if");
      //event.preventDefault();
    }
     else {
      console.log("que wea 2.0")
      axios.post('http://localhost:5000/saveEncuesta', {dict} )
         .then(res => {
           console.log(res);
           alert("Enviado Correctamente")
         })
    
       handleClose(true);
       //event.preventDefault();
      }
    */
  }

  return (
      <>
        <Button variant="primary" size="lg" onClick={handleShow} className="mb-3">
          Agregar Nueva Encuesta
        </Button>

        <Modal show={show} onHide={handleClose} backdrop="static">
          <Modal.Header closeButton>
            <Modal.Title>Agregar Nueva Encuesta</Modal.Title>
          </Modal.Header>
          <Form onSubmit={handleSubmit}>
            <Modal.Body>
              <InputGroup className="mb-3">
                <Form.Control 
                  required
                  name="titulo_encuesta" 
                  placeholder="Título" aria-label="Título"
                  aria-describedby="basic-addon2" 
                  size="lg" 
                  type="text" 
                  autoFocus 
                  onChange={handleChange}/>
              </InputGroup>
              <InputGroup className="mb-3">
                <Form.Control 
                  required
                  name="descripcion_encuesta" 
                  placeholder="Descripción" 
                  aria-label="Descripción"
                  aria-describedby="basic-addon2" 
                  as="textarea" 
                  rows={3} 
                  type="text" 
                  autoFocus
                  onChange={handleChange}/>
              </InputGroup>
              <Form.Group className="mb-3">
                <Form.Label>Seleccione Etiqueta</Form.Label>
                <Form.Select name="tag_encuesta" onChange={handleChange}>
                  <option selected disabled hidden value="none"> ---Seleccionar---</option>
                  {etiquetas}
                </Form.Select>
              </Form.Group>
              {cardList}
              <Button variant="info" onClick={onAddCardClick}>Agregar Pregunta</Button>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={vaciarCardListCancelar}>Cancelar</Button>
              <Button variant="primary" type="submit">Guardar Encuesta</Button>
            </Modal.Footer>
          </Form>
        </Modal>
      </>
  );
}

export default ModalAgregarEncuesta;