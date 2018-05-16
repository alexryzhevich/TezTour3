import React from 'react';
import { Button } from 'reactstrap';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import PrioritiesModal from '../priorities-modal';
import { apiPost } from '../../../actions/api';
import { toServerFormat } from '../../util/formatData';
import {
  openEditPrioritiesMode,
  togglePrioritiesModal,
  closeEditPrioritiesMode,
  handlePrecomputedData
} from '../../../actions/layout';
import { toggleLoading } from '../../../actions/ui';
import { withConfirm } from '../../util/hoc';
import {
  EDIT_DATES_PRIORITIES,
  CANCEL_BUTTON_TITLE,
  DESCRIPTION_FOR_EDIT_PRIORITIES
} from '../../../constants/constants';

import { PRECOMPUTE_URL } from '../../../api/Navigation';

class EditPrioritiesMode extends React.Component {
  constructor(props) {
    super(props);

    this.precompute = this.precompute.bind(this);
  }

  precompute(datesPriorities) {
    const {
      formattedData, serverData, newPriorities, selectedDates
    } = this.props.data;
    const reformattedData = toServerFormat(
      formattedData,
      serverData,
      newPriorities,
      selectedDates,
      datesPriorities
    );

    this.props.apiPost(
      PRECOMPUTE_URL,
      reformattedData,
      this.props.handlePrecomputedData,
      null,
      null,
      true
    );
    this.props.closeEditPrioritiesMode();
  }

  render() {
    const { togglePrioritiesModal } = this.props;
    return (
      <div>
        <Button color="secondary" onClick={togglePrioritiesModal}>
          {EDIT_DATES_PRIORITIES}
        </Button>
        <Button color="secondary" onClick={this.props.closeEditPrioritiesMode}>
          {CANCEL_BUTTON_TITLE}
        </Button>
        <PrioritiesModal onSubmit={this.precompute} description={DESCRIPTION_FOR_EDIT_PRIORITIES} />
      </div>
    );
  }
}

const mapStateToProps = state => ({
  data: state.layout.data
});

const mapDispatchToProps = dispatch => bindActionCreators({
  togglePrioritiesModal,
  handlePrecomputedData,
  openEditPrioritiesMode,
  closeEditPrioritiesMode,
  toggleLoading,
  apiPost,
}, dispatch);

const ConnectedEditPrioritiesMode = connect(mapStateToProps, mapDispatchToProps)(EditPrioritiesMode);

export default withConfirm(ConnectedEditPrioritiesMode);
