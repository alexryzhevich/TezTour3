import React from 'react';
import { Button, Form, Row, Col } from 'reactstrap';
import { connect } from 'react-redux';
import { FieldArray, reduxForm } from 'redux-form';

import PrioritiesTotalInfo from './PrioritiesTotalInfo';
import validate from '../utils/validatePriorities';

import {
  CANCEL_BUTTON_TITLE,
  PRIORITIES,
  SAVE_BUTTON_TITLE,
} from '../../../constants/constants';

const Buttons = ({ hasErrors, toggle }) => (
  <Row>
    <Col md={4}>
      <Button color="default" onClick={toggle}>{CANCEL_BUTTON_TITLE}</Button>
    </Col>
    <Col md={4} />
    <Col md={4}>
      <Button color="primary" type="submit" disabled={hasErrors}>{SAVE_BUTTON_TITLE}</Button>
    </Col>
  </Row>
);

const PrioritiesForm = ({
  invalid, fields, handleSubmit, maxDays, minDays, priorities, description, toggle
}) => (
  <Row>
    <Col md={12}>
      <Form onSubmit={handleSubmit}>
        <FieldArray
          name="priorities"
          component={PrioritiesTotalInfo}
          description={description}
          props={{
            ...fields, maxDays, minDays, priorities
          }}
        />
        <Buttons hasErrors={invalid} toggle={toggle} />
      </Form>
    </Col>
  </Row>
);

const ReduxForm = reduxForm({
  form: PRIORITIES,
  destroyOnUnmount: false,
  validate
})(PrioritiesForm);

function mapStateToProps(props) {
  const { maxDays, minDays, priorities } = props;
  return {
    fields: {
      maxDays,
      minDays,
      priorities
    }
  };
}

export default connect(mapStateToProps)(ReduxForm);
