import React from 'react';
import { Button, Form, Row, Col } from 'reactstrap';
import { connect } from 'react-redux';
import { FieldArray, reduxForm, formValueSelector } from 'redux-form';
import Priorities from './Priorities';
import PrioritiesDescription from '../utils/PrioritiesDescription';
import validate from '../utils/validatePriorities';
import { DESCRIPTION_ENTER_PRIORITIES } from '../../../constants/constants';

const ButtonGroup = ({ handlePreviousStep, hasErrors }) => (
  <Row>
    <Col md={4}>
      <Button onClick={handlePreviousStep}>
        Назад
      </Button>
    </Col>
    <Col md={4} />
    <Col md={4}>
      <Button
        type="submit"
        disabled={hasErrors}
      >
        Далее
      </Button>
    </Col>
  </Row>
);


const PrioritiesStep = ({
  invalid, fields, handlePreviousStep, handleSubmit
}) => (
  <span>
    <Row>
      <Col md={12}>
        <h3> Шаг 2: Приоритеты</h3>
      </Col>
    </Row>
    <Row>
      <Col md={12}>
        <PrioritiesDescription
          priorities={fields.priorities}
          description={DESCRIPTION_ENTER_PRIORITIES}
        />
      </Col>
    </Row>
    <Row>
      <Col md={2} />
      <Col md={8}>
        <Form onSubmit={handleSubmit}>
          <FieldArray
            name="priorities"
            component={Priorities}
            props={{ ...fields }}
          />
          <ButtonGroup
            handlePreviousStep={handlePreviousStep}
            hasErrors={invalid}
          />
        </Form>
      </Col>
      <Col md={2} />
    </Row>
  </span>

);

const selector = formValueSelector('wizard');

const ReduxForm = reduxForm({
  form: 'wizard',
  destroyOnUnmount: false,
  validate
})(PrioritiesStep);

const mapStateToProps = state => ({
  fields: {
    maxDays: selector(state, 'maxDays'),
    minDays: selector(state, 'minDays'),
    priorities: state.form && state.form.wizard && state.form.wizard.values && state.form.wizard.values.priorities ? state.form.wizard.values.priorities : [],
  }
});

export default connect(mapStateToProps)(ReduxForm);
