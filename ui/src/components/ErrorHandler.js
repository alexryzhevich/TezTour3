import React from 'react';
import { Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Button, Modal, ModalBody, ModalFooter } from 'reactstrap';
import { setError } from '../actions/ui';
import ERRORS from './util/error/errorMessages';
import { CLOSE_BUTTON_TITLE } from '../constants/constants';

const REDIRECTION_STATUS_CODES = [401, 404];

const getErrorMessage = (error) => {
  if (!error) {
    return null;
  }
  if (error.status !== 400) {
    return ERRORS.messages[ERRORS.codes.UNKNOWN_ERROR];
  }
  return ERRORS.messages[error.data.code] || error.data.message;
};

class ErrorHandler extends React.PureComponent {
  constructor(props) {
    super(props);

    this.setError = this.setError.bind(this);
    this.resetError = this.resetError.bind(this);
    this.renderRedirection = this.renderRedirection.bind(this);
  }

  setError(error) {
    console.log(error);
    this.props.setError(error);
  }

  resetError() {
    this.props.setError(null);
  }

  renderRedirection(statusCode) {
    const statusFuncs = {
      401: () => <Redirect to="/login" />,
      404: () => <Redirect to="/error/404" />
    };

    return statusFuncs[statusCode]();
  }

  render() {
    const { error } = this.props;

    if (!!error && REDIRECTION_STATUS_CODES.includes(error.status)) {
      return this.renderRedirection(error.status);
    }

    const errorMessage = getErrorMessage(error);

    return (
      <Modal isOpen={!!errorMessage} toggle={this.resetError}>
        <ModalBody>
          {errorMessage}
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={this.resetError}>{CLOSE_BUTTON_TITLE}</Button>
        </ModalFooter>
      </Modal>
    );
  }
}

const mapStateToProps = state => ({
  error: state.ui.error
});

const mapDispatchToProps = dispatch => bindActionCreators({ setError }, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(ErrorHandler);
