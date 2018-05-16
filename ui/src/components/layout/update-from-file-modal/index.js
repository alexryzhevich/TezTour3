import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Modal, ModalBody, ModalFooter, Button, ModalHeader } from 'reactstrap';
import { apiPut } from '../../../actions/api';
import Dropzone from '../../form/dropzone';
import { toggleLoading } from '../../../actions/ui';
import { toggleUpdateFromFileModal, updateLayoutData } from '../../../actions/layout';
import {
  UPDATE_BUTTON_TITLE,
  CANCEL_BUTTON_TITLE,
  UPDATING_LAYOUT_FROM_FILE_LABEL
} from '../../../constants/constants';
import { getLayoutUpdateUrl } from '../../../api/Navigation';


class UpdateFromFileForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      accepted: [],
      rejected: [],
      formData: null
    };

    this.onDrop = this.onDrop.bind(this);
    this.updateFromFile = this.updateFromFile.bind(this);
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
    const { layoutId, apiPut } = this.props;
    const { isEnabled, editToken, hasChanges } = this.props.editMode;

    if (hasChanges || !isEnabled || !formData) {
      return;
    }

    const url = getLayoutUpdateUrl(layoutId);

    const headers = {
      'Content-Type': 'multipart/form-data',
      'Edit-token': editToken
    };
    apiPut(url, formData, this.props.updateLayoutData, null, headers, true);
    this.props.toggleUpdateFromFileModal();
  }

  render() {
    const { accepted, rejected, formData } = this.state;
    const { modal } = this.props;
    const { isUpdateFromFileModalOpen } = modal;

    return (
      <Modal isOpen={isUpdateFromFileModalOpen} toggle={this.props.toggleUpdateFromFileModal}>
        <ModalHeader>
          {UPDATING_LAYOUT_FROM_FILE_LABEL}
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
            onClick={this.props.toggleUpdateFromFileModal}
          >
            {CANCEL_BUTTON_TITLE}
          </Button>
          <Button
            color="primary"
            onClick={this.updateFromFile}
            disabled={!formData}
          >
            {UPDATE_BUTTON_TITLE}
          </Button>
        </ModalFooter>
      </Modal>
    );
  }
}

const mapStateToProps = state => ({
  modal: state.layout.modal,
  editMode: state.layout.toolbar.editMode
});


const mapDispatchToProps = dispatch => bindActionCreators({
  toggleLoading, updateLayoutData, toggleUpdateFromFileModal, apiPut
}, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(UpdateFromFileForm);
