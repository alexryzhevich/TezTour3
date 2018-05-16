import React from 'react';
import { Button, Label, Form, FormGroup, Col, Row } from 'reactstrap';
import { Field, reduxForm } from 'redux-form';
import { connect } from 'react-redux';
import renderInput from '../utils/renderInput';
import { required, minValue, maxValue, integer } from '../../util/validations';
import {
  AMOUNT_DAYS,
  FIRST_STEP_LABEL,
  INCORRECT_VALUE,
  MAX_LABEL,
  MIN_LABEL,
  ARRIVAL_PLACE_LABEL,
  DEPARTURE_PLACE_LABEL,
  DURATION_LIMIT_LABEL,
  WIZARD,
} from '../../../constants/constants';

const MIN_DAYS_VALUE = 2;
const MAX_DAYS_VALUE = 22;
const DEFAULT_MIN_DAYS_VALUE = 7;
const DEFAULT_MAX_DAYS_VALUE = 14;


const validate = ({ minDays, maxDays, durationLimit }) => {
  if (Number(minDays) >= Number(maxDays)) {
    return {
      minDays: INCORRECT_VALUE,
      maxDays: INCORRECT_VALUE
    };
  }
  if (Number(durationLimit) < maxDays) {
    return {
      durationLimit: INCORRECT_VALUE
    };
  }
  return {};
};


const SubmitButton = ({ hasErrors }) => (
  <Row>
    <Col md={8} />
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


const LayoutInfoStep = ({ invalid, handleSubmit }) => (
  <Row>
    <Col md={2} />
    <Col md={8}>
      <Form onSubmit={handleSubmit}>
        <h3> {FIRST_STEP_LABEL} </h3>
        <FormGroup row>
          <Label
            for="arrivalPlace"
            sm={4}
          >
            {ARRIVAL_PLACE_LABEL}
          </Label>
          <Col sm={8}>
            <Field
              name="arrivalPlace"
              type="text"
              validate={required}
              component={renderInput}
            />
          </Col>
        </FormGroup>
        <FormGroup row>
          <Label
            for="departurePlace"
            sm={4}
          >
            {DEPARTURE_PLACE_LABEL}
          </Label>
          <Col sm={8}>
            <Field
              name="departurePlace"
              type="text"
              validate={required}
              component={renderInput}
            />
          </Col>
        </FormGroup>
        <FormGroup row>
          <Label
            sm={4}
          >
            {AMOUNT_DAYS}
          </Label>
          <Col sm={4}>
            <Field
              name="minDays"
              type="text"
              validate={[integer, minValue(MIN_DAYS_VALUE)]}
              component={renderInput}
              label={MIN_LABEL}
            />
          </Col>
          <Col sm={4}>
            <Field
              name="maxDays"
              type="text"
              validate={[integer, maxValue(MAX_DAYS_VALUE)]}
              component={renderInput}
              label={MAX_LABEL}
            />
          </Col>
        </FormGroup>
        <FormGroup row>
          <Label
            for="durationLimit"
            sm={4}
          >
            {DURATION_LIMIT_LABEL}
          </Label>
          <Col sm={4}>
            <Field
              name="durationLimit"
              type="text"
              validate={[integer, maxValue(MAX_DAYS_VALUE)]}
              component={renderInput}
            />
          </Col>
        </FormGroup>
        <SubmitButton hasErrors={invalid} />
      </Form>
    </Col>
    <Col md={2} />
  </Row>
);

const InitializedForm = reduxForm({
  form: WIZARD,
  destroyOnUnmount: false,
  validate
})(LayoutInfoStep);

const mapStateToProps = () => ({
  initialValues: {
    minDays: DEFAULT_MIN_DAYS_VALUE,
    maxDays: DEFAULT_MAX_DAYS_VALUE
  }
});

export default connect(mapStateToProps)(InitializedForm);
