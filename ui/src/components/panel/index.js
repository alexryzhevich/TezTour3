import React from 'react';
import { Container, Row } from 'reactstrap';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import PanelHeader from './Header';
import Card from './card';
import { withConfirm } from '../util/hoc';
import { apiGet, apiDelete } from '../../actions/api';
import { WARNING_FOR_DELETE_LAYOUT } from '../../constants/constants';
import { LAYOUTS_URL, deleteLayoutUrl } from '../../api/Navigation';

class LayoutPanel extends React.Component {
  constructor(props) {
    super(props);

    this.state = {};

    this.deleteLayout = this.deleteLayout.bind(this);
    this.loadLayouts = this.loadLayouts.bind(this);
  }

  componentDidMount() {
    this.loadLayouts();
  }

  deleteLayout(id) {
    return () => {
      const { showConfirm, apiDelete } = this.props;

      showConfirm(
        WARNING_FOR_DELETE_LAYOUT,
        () => apiDelete(deleteLayoutUrl(id), this.loadLayouts)
      );
    };
  }

  loadLayouts() {
    this.props.apiGet(LAYOUTS_URL, data => this.setState({ data }), null, null, true);
  }

  render() {
    const { data } = this.state;
    if (!data) {
      return null;
    }

    const { layouts } = data;

    const cards = layouts.map(item => (
      <Card key={item.id} {...item} deleteLayout={this.deleteLayout} />
    ));

    return (
      <Container>
        <PanelHeader />
        <Row>
          { cards }
        </Row>
      </Container>
    );
  }
}

const mapDispatchToProps = dispatch => bindActionCreators({
  apiGet,
  apiDelete
}, dispatch);

const WrappedPanel = withConfirm(LayoutPanel);

export default connect(null, mapDispatchToProps)(WrappedPanel);
