import React from 'react';
import { Card, Button, CardBody, CardTitle, CardText, Col } from 'reactstrap';
import { GoX } from 'react-icons/lib/go';
import { goToInitializationStep } from '../../../api/Navigation';
import {
  OPEN_BUTTON_TITLE,
  CONTINUE_CREATING_BUTTON_TITLE,
  UPDATE_FROM_FILE_DATE
  // START_DATE,
  // END_DATE
} from '../../../constants/constants';
import './Card.css';

const LAYOUT_URL = '/layouts';

const openLayout = id => () => { window.location = `${LAYOUT_URL}/${id}`; };

const formatDate = value => (value ? new Date(value).toLocaleDateString('ru-RU') : value);

const LayoutCard = ({
  id, name, startDate, endDate, deleteLayout, updateFromFileDate
}) => {
  const startEndDateLabel = startDate && endDate ? `${formatDate(startDate)} — ${formatDate(endDate)}` : '';
  const lastUpdateDateLabel = updateFromFileDate ? `${UPDATE_FROM_FILE_DATE}: ${formatDate(updateFromFileDate)}` : '';
  const initialized = !!startDate;

  return (
    <Col md={6} lg={4}>
      <Card className="Card" color={initialized ? 'default' : 'warning'}>
        <CardBody>
          <GoX className="remove-icon" onClick={deleteLayout(id)} />
          <CardTitle>
            { name }
          </CardTitle>
          <CardText>
            { startEndDateLabel }
          </CardText>
          <CardText>
            { lastUpdateDateLabel }
          </CardText>
          <Button outline={!initialized} onClick={initialized ? openLayout(id) : goToInitializationStep(id)}>
            { initialized ? OPEN_BUTTON_TITLE : CONTINUE_CREATING_BUTTON_TITLE}
          </Button>
        </CardBody>
      </Card>
    </Col>
  );
};

export default LayoutCard;
