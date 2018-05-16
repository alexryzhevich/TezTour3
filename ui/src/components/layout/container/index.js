import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import Toolbar from '../toolbar';
import Layout from '../Layout';
import LossesTab from '../losses';
import { updateLayoutData, resetEditMode } from '../../../actions/layout';
import { apiGet, apiDelete } from '../../../actions/api';
import { getLayoutUrl, getExtendEditModeUrl } from '../../../api/Navigation';
import './Container.css';


class LayoutContainer extends React.Component {
  constructor(props) {
    super(props);

    this.loadLayoutData = this.loadLayoutData.bind(this);
    this.closeEditMode = this.closeEditMode.bind(this);
  }

  componentDidMount() {
    this.loadLayoutData();
  }

  componentWillUnmount() {
    this.closeEditMode();
  }

  loadLayoutData() {
    const { apiGet, updateLayoutData, match } = this.props;
    const { id } = match.params;

    apiGet(getLayoutUrl(id), updateLayoutData, null, null, true);
  }

  closeEditMode() {
    const { apiDelete, resetEditMode } = this.props;
    const { id } = this.props.match.params;
    const { editToken } = this.props.editMode;

    const headers = {
      'Edit-token': editToken
    };
    apiDelete(getExtendEditModeUrl(id), null, null, headers);

    resetEditMode();
    this.loadLayoutData();
  }

  render() {
    return (
      <div className="layout-container">
        <Toolbar
          loadLayoutData={this.loadLayoutData}
          closeEditMode={this.closeEditMode}
        />
        <LossesTab />
        <Layout />
      </div>
    );
  }
}

const mapStateToProps = state => ({
  editMode: state.layout.toolbar.editMode
});

const mapDispatchToProps = dispatch => bindActionCreators({
  updateLayoutData,
  resetEditMode,
  apiGet,
  apiDelete
}, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(LayoutContainer);
