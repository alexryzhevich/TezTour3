import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Container } from 'reactstrap';
import LayoutInfoStep from './wizard/LayoutInfoStep';
import PrioritiesStep from './wizard/PrioritiesStep';
import { apiPost } from '../../actions/api';
import {
  LAYOUTS_URL,
  goToInitializationStep
} from '../../api/Navigation';

const formatLayoutName = (arrivalPlace, departurePlace) => `${arrivalPlace} -> ${departurePlace}`;


class LayoutForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      page: 1
    };

    this.nextPage = this.nextPage.bind(this);
    this.previousPage = this.previousPage.bind(this);
    this.handleSubmitInfo = this.handleSubmitInfo.bind(this);
  }
  nextPage() {
    this.setState({ page: this.state.page + 1 });
  }

  previousPage() {
    this.setState({ page: this.state.page - 1 });
  }

  handleSubmitInfo(values) {
    const data = {
      name: formatLayoutName(values.arrivalPlace, values.departurePlace),
      maxDays: values.maxDays,
      minDays: values.minDays,
      durationLimit: values.durationLimit,
      priorities: values.priorities
    };

    this.props.apiPost(
      LAYOUTS_URL,
      data,
      (layout) => {
        const { id } = layout;
        goToInitializationStep(id)();
      }
    );
  }

  render() {
    const { page } = this.state;

    return (
      <Container>
        {
          page === 1 && <LayoutInfoStep onSubmit={this.nextPage} />
        }
        {
          page === 2 && (
            <PrioritiesStep
              handlePreviousStep={this.previousPage}
              onSubmit={this.handleSubmitInfo}
            />
          )
        }
      </Container>
    );
  }
}

const mapDispatchToProps = dispatch => bindActionCreators({
  apiPost,
}, dispatch);

export default connect(null, mapDispatchToProps)(LayoutForm);
