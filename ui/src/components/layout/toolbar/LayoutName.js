import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { FaCaretDown, FaCaretUp } from 'react-icons/lib/fa';
import { toggleShowLosses } from '../../../actions/layout';

const formatDate = value => (value ? new Date(value).toLocaleDateString('ru-RU') : value);

class LayoutName extends React.Component {
  renderShowLossesIcon() {
    const { toggleShowLosses } = this.props;
    const { show: isLossesTabActive } = this.props.lossesTab;
    const { hasChanges: cannotShowLosses } = this.props.editMode;
    if (cannotShowLosses) {
      return null;
    }
    const props = {
      className: 'icon-btn',
      onClick: toggleShowLosses
    };
    return isLossesTabActive ? <FaCaretUp {...props} /> : <FaCaretDown {...props} />;
  }

  render() {
    const { layoutName, updateFromFileDate } = this.props;
    const lastUpdateDateLabel = updateFromFileDate ? ` (${formatDate(updateFromFileDate)})` : '';

    return <h4>{layoutName}{lastUpdateDateLabel}{this.renderShowLossesIcon()}</h4>;
  }
}

const mapStateToProps = state => ({
  lossesTab: state.layout.toolbar.lossesTab,
  editMode: state.layout.toolbar.editMode
});

const mapDispatchToProps = dispatch => bindActionCreators({
  toggleShowLosses
}, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(LayoutName);
