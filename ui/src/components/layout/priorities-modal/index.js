import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Modal, ModalBody } from 'reactstrap';
import PrioritiesForm from '../../form/priorities/PrioritiesForm';
import { togglePrioritiesModal } from '../../../actions/layout';
import './Modal.css';


class PrioritiesModal extends React.PureComponent {
  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(form) {
    const newPriorities = form.priorities.map(priority => Number(priority));

    this.props.onSubmit(newPriorities);
  }

  render() {
    const {
      data, description, newPriorities, modal, togglePrioritiesModal
    } = this.props;
    const { isPrioritiesModalOpen } = modal;
    const { priorities, maxDays, minDays } = data;
    return (
      <Modal isOpen={isPrioritiesModalOpen} toggle={togglePrioritiesModal}>
        <ModalBody>
          <PrioritiesForm
            priorities={newPriorities || priorities}
            maxDays={maxDays}
            minDays={minDays}
            toggle={togglePrioritiesModal}
            onSubmit={this.handleSubmit}
            description={description}
          />
        </ModalBody>
      </Modal>
    );
  }
}

const mapStateToProps = state => ({
  modal: state.layout.modal,
  data: state.layout.data.serverData,
  newPriorities: state.layout.data.newPriorities
});

const mapDispatchToProps = dispatch => bindActionCreators({
  togglePrioritiesModal
}, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(PrioritiesModal);
