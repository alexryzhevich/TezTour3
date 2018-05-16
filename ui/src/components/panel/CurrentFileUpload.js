import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Modal, ModalBody, ModalFooter, Button, ModalHeader } from 'reactstrap';
import { apiPost } from '../../actions/api';
import Dropzone from '../form/dropzone';
import {
  UPLOAD_BUTTON_TITLE,
  UPLOAD_CURRENT_FILE_BUTTON_LABEL,
  CANCEL_BUTTON_TITLE,
  UPLOADING_NEW_CURRENT_FILE_LABEL,
} from '../../constants/constants';
import { UPLOAD_CURRENT_FILE_URL } from '../../api/Navigation';


class UpdateFromFileForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      accepted: [],
      rejected: [],
      formData: null,
      isModalOpen: false,
    };

    this.onDrop = this.onDrop.bind(this);
    this.updateFromFile = this.updateFromFile.bind(this);
    this.toggleModal = this.toggleModal.bind(this);
  }

  onDrop(accepted, rejected) {
    this.setState({ accepted, rejected });
    if (accepted.length) {
      const formData = new FormData();
      formData.append('file', accepted[0]);
      this.setState({ formData });
    }
  }

  updateFromFile() {
    const { formData } = this.state;
    const { apiPost } = this.props;

    if (!formData) {
      return;
    }

    const headers = {
      'Content-Type': 'multipart/form-data',
    };
    apiPost(UPLOAD_CURRENT_FILE_URL, formData, null, null, headers, true);
    this.toggleModal();
  }

  toggleModal() {
    this.setState({ isModalOpen: !this.state.isModalOpen });
  }

  render() {
    const {
      accepted, rejected, formData, isModalOpen
    } = this.state;

    return (
      <div>
        <Button
          color="primary"
          onClick={this.toggleModal}
        >
          {UPLOAD_CURRENT_FILE_BUTTON_LABEL}
        </Button>
        <Modal isOpen={isModalOpen} toggle={this.toggleModal}>
          <ModalHeader>
            {UPLOADING_NEW_CURRENT_FILE_LABEL}
          </ModalHeader>
          <ModalBody>
            <Dropzone
              onDrop={this.onDrop}
              accepted={accepted}
              rejected={rejected}
            />
          </ModalBody>
          <ModalFooter>
            <Button
              color="secondary"
              onClick={this.toggleModal}
            >
              {CANCEL_BUTTON_TITLE}
            </Button>
            <Button
              color="primary"
              onClick={this.updateFromFile}
              disabled={!formData}
            >
              {UPLOAD_BUTTON_TITLE}
            </Button>
          </ModalFooter>
        </Modal>
      </div>
    );
  }
}


const mapDispatchToProps = dispatch => bindActionCreators({
  apiPost
}, dispatch);

export default connect(null, mapDispatchToProps)(UpdateFromFileForm);
