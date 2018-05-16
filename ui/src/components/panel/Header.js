import React from 'react';
import { Row, Col, Button } from 'reactstrap';
import { ADD_LAYOUT_BUTTON_TITLE } from '../../constants/constants';
import { goToLayoutCreation } from '../../api/Navigation';
import CurrentFileUpload from './CurrentFileUpload';


const Header = () => (
  <Row>
    <Col md={3}>
      <Button
        color="success"
        onClick={goToLayoutCreation}
      >
        {ADD_LAYOUT_BUTTON_TITLE}
      </Button>
    </Col>
    <Col md={6}>
      <h3> Раскладки </h3>
    </Col>
    <Col md={3}>
      <CurrentFileUpload />
    </Col>
  </Row>
);

export default Header;
