import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Container, Col, Row } from 'reactstrap';
import { apiPost } from '../../actions/api';
import Dropzone from './dropzone';
import { goToLayout, getLayoutUpdateUrl } from '../../api/Navigation';

class UploadForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      accepted: [],
      rejected: []
    };

    this.onDrop = this.onDrop.bind(this);
    this.handleResponse = this.handleResponse.bind(this);
  }

  onDrop(accepted, rejected) {
    this.setState({ accepted, rejected });
    if (accepted.length) {
      const { apiPost } = this.props;
      const { id } = this.props.match.params;
      const url = getLayoutUpdateUrl(id);

      const formData = new FormData();
      formData.append('file', accepted[0]);
      const headers = {
        'Content-Type': 'multipart/form-data'
      };
      apiPost(
        url,
        formData,
        this.handleResponse,
        null,
        headers,
        true
      );
    }
  }

  handleResponse(data) {
    const { id } = data;
    goToLayout(id);
  }

  render() {
    const { accepted, rejected } = this.state;

    return (
      <Container>
        <h3> Шаг 3: Загрузка файла Excel</h3>
        <Row>
          <Col md={3} />
          <Col md={6}>
            <Dropzone
              onDrop={this.onDrop}
              accepted={accepted}
              rejected={rejected}
            />
          </Col>
          <Col md={3} />
        </Row>
      </Container>
    );
  }
}

const mapDispatchToProps = dispatch => bindActionCreators({ apiPost }, dispatch);

export default connect(null, mapDispatchToProps)(UploadForm);
