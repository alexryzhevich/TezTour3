import React from 'react';
import { Button, Modal, ModalBody, ModalFooter } from 'reactstrap';
import {
  CANCEL_BUTTON_TITLE,
  YES_BUTTON_TITLE
} from '../../../constants/constants';

const withConfirm = (WrapperComponent) => {
  class ConfirmWrapper extends React.Component {
    constructor(props) {
      super(props);
      this.state = {};

      this.showConfirm = this.showConfirm.bind(this);
      this.hide = this.hide.bind(this);
      this.confirm = this.confirm.bind(this);
    }

    showConfirm(message, onConfirm) {
      this.setState({ message, onConfirm });
    }

    hide() {
      this.showConfirm(null, null);
    }

    confirm() {
      const { onConfirm } = this.state;
      if (onConfirm) {
        onConfirm();
      }
      this.hide();
    }

    render() {
      const { message } = this.state;

      return (
        <div>
          <WrapperComponent {...this.props} showConfirm={this.showConfirm} />
          <Modal isOpen={!!message} toggle={this.hide}>
            <ModalBody>
              {message}
            </ModalBody>
            <ModalFooter>
              <Button color="secondary" onClick={this.hide}>{CANCEL_BUTTON_TITLE}</Button>
              <Button color="danger" onClick={this.confirm}>{YES_BUTTON_TITLE}</Button>
            </ModalFooter>
          </Modal>
        </div>
      );
    }
  }

  return ConfirmWrapper;
};

export default withConfirm;
