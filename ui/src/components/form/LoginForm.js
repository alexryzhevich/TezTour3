import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { reduxForm, Field } from 'redux-form';
import { Col, Row, Form, FormGroup, Button, Label } from 'reactstrap';
import { toggleLoading, setError } from '../../actions/ui';
import renderInput from './utils/renderInput';
import { required } from '../util/validations';
import { LOGIN, USERNAME_LABEL, PASSWORD_LABEL, LOGIN_BUTTON_TITLE } from '../../constants/constants';


const SubmitButton = ({ hasErrors }) => (
  <Row>
    <Col md={4} />
    <Col md={4}>
      <Button
        type="submit"
        disabled={hasErrors}
      >
        { LOGIN_BUTTON_TITLE }
      </Button>
    </Col>
    <Col md={4} />
  </Row>
);


const LoginForm = ({ handleSubmit, invalid }) => (
  <Form onSubmit={handleSubmit}>
    <h3> Логин </h3>
    <FormGroup row>
      <Label
        for="username"
        sm={4}
      >
        {USERNAME_LABEL}
      </Label>
      <Col sm={8}>
        <Field
          name="username"
          type="text"
          validate={required}
          component={renderInput}
        />
      </Col>
    </FormGroup>
    <FormGroup row>
      <Label
        for="password"
        sm={4}
      >
        {PASSWORD_LABEL}
      </Label>
      <Col sm={8}>
        <Field
          name="password"
          type="password"
          validate={required}
          component={renderInput}
        />
      </Col>
    </FormGroup>
    <SubmitButton hasErrors={invalid} />
  </Form>
);

const InitializedForm = reduxForm({
  form: LOGIN,
  destroyOnUnmount: false
})(LoginForm);

const mapDispatchToProps = dispatch => bindActionCreators({ toggleLoading, setError }, dispatch);

export default connect(null, mapDispatchToProps)(InitializedForm);
