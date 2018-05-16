import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import EditModePanel from './EditModePanel';
import PrioritiesModal from '../../priorities-modal';
import LossesModal from '../../losses-modal';
import UpdateFromFileModal from '../../update-from-file-modal';
import { apiPost } from '../../../../actions/api';
import { toServerFormat } from '../../../util/formatData';
import { toggleLoading } from '../../../../actions/ui';
import { withConfirm } from '../../../util/hoc';
import {
  updateLayoutData,
  toggleAutoPrecompute,
  handlePrecomputedData,
  togglePrioritiesModal,
  toggleLossesModal,
  toggleUpdateFromFileModal,
  openEditPrioritiesMode,
  saveLayoutPriorities
} from '../../../../actions/layout';
import {
  WARNING_FOR_RESET,
  DESCRIPTION_FOR_EDIT_PRIORITIES
} from '../../../../constants/constants';
import { PRECOMPUTE_URL, getLayoutUpdateFromCurrentFileUrl } from '../../../../api/Navigation';

const EXTEND_EDIT_MODE_INTERVAL = 30000;

class EditMode extends React.Component {
  constructor(props) {
    super(props);

    this.toggleAutoPrecompute = this.toggleAutoPrecompute.bind(this);
    this.precompute = this.precompute.bind(this);
    this.reset = this.reset.bind(this);
    this.saveLayoutPriorities = this.saveLayoutPriorities.bind(this);
    this.saveLosses = this.saveLosses.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.handleEditModeOpen = this.handleEditModeOpen.bind(this);
    this.updateFromCurrentFile = this.updateFromCurrentFile.bind(this);
  }

  toggleAutoPrecompute(e) {
    if (e.target.checked) {
      this.precompute();
    }
    this.props.toggleAutoPrecompute();
  }

  precompute() {
    const { formattedData, serverData, newPriorities } = this.props.data;
    const { hasChanges } = this.props.editMode;

    if (!hasChanges) {
      return;
    }

    const reformattedData = toServerFormat(formattedData, serverData, newPriorities);
    this.props.apiPost(
      PRECOMPUTE_URL,
      reformattedData,
      this.props.handlePrecomputedData,
      null,
      null,
      true
    );
  }

  reset() {
    this.props.showConfirm(WARNING_FOR_RESET, this.handleReset);
  }

  handleReset() {
    const { formattedData, serverData } = this.props.data;
    const { isEnabled } = this.props.editMode;
    const data = [...formattedData];

    if (!isEnabled) {
      return;
    }

    for (let i = 0; i < data.length; i += 1) {
      data[i].priorities = null;
      for (let j = 0; j < data[i].places.length; j += 1) {
        data[i].places[j].required = false;
      }
    }
    const reformattedData = toServerFormat(data, serverData);
    this.props.apiPost(
      PRECOMPUTE_URL,
      reformattedData,
      this.props.handlePrecomputedData,
      null,
      null,
      true
    );
  }

  handleEditModeOpen(tokenData) {
    const { editToken } = this.props.editMode;

    const extendTimeout = setTimeout(this.openEditMode, EXTEND_EDIT_MODE_INTERVAL);

    this.props.openEditMode({
      editToken: tokenData.token || editToken,
      extendTimeout
    });
  }

  updateFromCurrentFile() {
    const { isEnabled, editToken, hasChanges } = this.props.editMode;
    const { serverData } = this.props.data;

    if (hasChanges || !isEnabled) {
      return;
    }

    const url = getLayoutUpdateFromCurrentFileUrl(serverData.id);

    const headers = {
      'Edit-token': editToken
    };
    this.props.apiPost(url, null, this.props.updateLayoutData, null, headers, true);
  }

  saveLayoutPriorities(newPriorities) {
    const { saveLayoutPriorities, apiPost } = this.props;
    saveLayoutPriorities(newPriorities);
    const { formattedData, serverData } = this.props.data;
    const reformattedData = toServerFormat(formattedData, serverData, newPriorities);
    apiPost(
      PRECOMPUTE_URL,
      reformattedData,
      this.props.handlePrecomputedData,
      null,
      null,
      true
    );
  }

  saveLosses(noLosses) {
    // console.log(noLosses);
    const { apiPost } = this.props;
    const { formattedData, serverData } = this.props.data;
    const reformattedData = toServerFormat(formattedData, serverData, null, [], [], noLosses);
    apiPost(
      PRECOMPUTE_URL,
      reformattedData,
      this.props.handlePrecomputedData,
      null,
      null,
      true
    );
  }

  render() {
    const {
      reset,
      toggleAutoPrecompute,
      precompute,
      updateFromCurrentFile
    } = this;
    const {
      openEditPrioritiesMode,
      openPrioritiesModal,
      openLossesModal,
      toggleUpdateFromFileModal
    } = this.props;
    const { id } = this.props.data.serverData;
    const {
      hasChanges,
      autoPrecompute,
      canSave
    } = this.props.editMode;

    const props = {
      panel: {
        hasChanges,
        autoPrecompute,
        canSave,
        toggleUpdateFromFileModal,
        openPrioritiesModal,
        openLossesModal,
        openEditPrioritiesMode,
        reset,
        toggleAutoPrecompute,
        precompute,
        updateFromCurrentFile,
      },
      modals: {
        priorities: {
          onSubmit: this.saveLayoutPriorities,
          description: DESCRIPTION_FOR_EDIT_PRIORITIES
        },
        losses: {
          onSubmit: this.saveLosses
        },
        file: {
          layoutId: id
        }
      }
    };

    return (
      <div>
        <EditModePanel {...props.panel} />
        <PrioritiesModal {...props.modals.priorities} />
        <LossesModal {...props.modals.losses} />
        <UpdateFromFileModal {...props.modals.file} />
      </div>
    );
  }
}

const mapStateToProps = state => ({
  editMode: state.layout.toolbar.editMode,
  data: state.layout.data
});

const mapDispatchToProps = dispatch => ({
  ...bindActionCreators({
    toggleLoading,
    updateLayoutData,
    toggleAutoPrecompute,
    handlePrecomputedData,
    saveLayoutPriorities,
    openEditPrioritiesMode,
    toggleUpdateFromFileModal,
    apiPost,
  }, dispatch),
  openPrioritiesModal: () => dispatch(togglePrioritiesModal()),
  openLossesModal: dateType => dispatch(toggleLossesModal(dateType))
});

const WrapperEditMode = withConfirm(EditMode);

export default connect(mapStateToProps, mapDispatchToProps)(WrapperEditMode);
