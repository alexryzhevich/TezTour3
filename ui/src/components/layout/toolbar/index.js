import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Card } from 'reactstrap';
import ExtendedBody from './ExtendedBody';
import ClosedBody from './ClosedBody';
import { apiPost } from '../../../actions/api';
import { toServerFormat } from '../../util/formatData';
import { withConfirm } from '../../util/hoc';
import { openEditMode, resetEditMode, updateLayoutData } from '../../../actions/layout';
import { toggleLoading } from '../../../actions/ui';
import './Toolbar.css';
import { WARNING_FOR_EXIT_WITHOUT_SAVE } from '../../../constants/constants';
import { getExtendEditModeUrl, getLayoutUrl } from '../../../api/Navigation';

const EXTEND_EDIT_MODE_INTERVAL = 30000;


class Toolbar extends React.PureComponent {
  constructor(props) {
    super(props);

    this.openEditMode = this.openEditMode.bind(this);
    this.closeEditMode = this.closeEditMode.bind(this);
    this.save = this.save.bind(this);
    this.handleEditModeOpen = this.handleEditModeOpen.bind(this);
  }

  openEditMode() {
    const { isEnabled, editToken } = this.props.editMode;
    const { id } = this.props.data.serverData;

    let headers = null;
    if (isEnabled) {
      headers = {
        'Edit-token': editToken
      };
    }
    this.props.apiPost(
      getExtendEditModeUrl(id),
      {},
      this.handleEditModeOpen,
      this.props.resetEditMode,
      headers
    );
  }

  closeEditMode() {
    const { canSave, hasChanges } = this.props.editMode;
    if (!canSave && !hasChanges) {
      this.props.closeEditMode();
      return;
    }
    this.props.showConfirm(WARNING_FOR_EXIT_WITHOUT_SAVE, this.props.closeEditMode);
  }

  save() {
    const { formattedData, serverData, newPriorities } = this.props.data;
    const { canSave, editToken } = this.props.editMode;

    if (!canSave) {
      return;
    }

    const headers = {
      'Edit-token': editToken
    };
    const reformattedData = toServerFormat(formattedData, serverData, newPriorities);
    this.props.apiPost(
      getLayoutUrl(serverData.id),
      reformattedData,
      this.props.updateLayoutData,
      null,
      headers,
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

  render() {
    const { isEditPrioritiesModeEnabled } = this.props;
    const { isEnabled: isEditModeEnabled, canSave } = this.props.editMode;
    const { name, updateFromFileDate } = this.props.data.serverData;

    const props = {
      closed: {
        layoutName: name,
        openEditMode: this.openEditMode,
        updateFromFileDate
      },
      extended: {
        canSave,
        isEditPrioritiesModeEnabled,
        closeEditMode: this.closeEditMode,
        layoutName: name,
        save: this.save,
        updateFromFileDate
      }
    };

    return (
      <Card className="toolbar">
        {
          isEditModeEnabled
            ? <ExtendedBody {...props.extended} />
            : <ClosedBody {...props.closed} />
        }
      </Card>
    );
  }
}

const mapStateToProps = state => ({
  editMode: state.layout.toolbar.editMode,
  isEditPrioritiesModeEnabled: state.layout.toolbar.editPrioritiesMode.isEnabled,
  data: state.layout.data
});

const mapDispatchToProps = dispatch => bindActionCreators({
  toggleLoading,
  openEditMode,
  resetEditMode,
  updateLayoutData,
  apiPost,
}, dispatch);

const WrappedToolbar = withConfirm(Toolbar);

export default connect(mapStateToProps, mapDispatchToProps)(WrappedToolbar);
