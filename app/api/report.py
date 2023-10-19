from app.bl.report.prepare import prepare
from app.api.utils.json_format import (
    json_response_api_report,
    json_response_api_drivers,
    json_response_api_driver
)
from app.api.utils.xml_format import (
    xml_response_api_report,
    xml_response_api_drivers,
    xml_response_api_driver
)
from flask import make_response, render_template, Response
from flask_restful import Resource, reqparse

PREPARED_DATA = prepare()

parser = reqparse.RequestParser()
parser.add_argument('format', type=str, location='args', default='json')
parser.add_argument('order', type=str, location='args', default='asc')


class Report(Resource):
    def get(self) -> Response:
        """
        This is the documentation for the /api/v1/report endpoint.

        GET:
        This operation retrieves a report.
        ---
        parameters:
          - name: format
            in: query
            type: string
            enum: ['json', 'xml']
            default: 'json'
          - name: order
            in: query
            type: string
            enum: ['asc', 'desc']
            default: 'asc'

        responses:
          200:
            description: Returns a report in the specified format.
            schema:
              type: object
              properties:
                data:
                  type: string
        """
        args = parser.parse_args()
        if args['order'] == 'desc':
            PREPARED_DATA.reverse()

        if args['format'] == 'xml':
            return xml_response_api_report(PREPARED_DATA)

        return json_response_api_report(PREPARED_DATA)


class Drivers(Resource):
    def get(self) -> Response:
        """
        This is the documentation for the /api/v1/drivers endpoint.

        GET:
        This operation retrieves statistics about drivers.
        ---
        parameters:
          - name: format
            in: query
            type: string
            enum: ['json', 'xml']
            default: 'json'
          - name: order
            in: query
            type: string
            enum: ['asc', 'desc']
            default: 'asc'

        responses:
          200:
            descriptions: Returns statistics about drivers
            schema:
              type: object
              properties:
                data:
                  type: string
        """
        args = parser.parse_args()
        if args['order'] == 'desc':
            PREPARED_DATA.reverse()

        if args['format'] == 'xml':
            return xml_response_api_drivers(PREPARED_DATA)

        return json_response_api_drivers(PREPARED_DATA)


class UniqueDriver(Resource):
    def get(self, driver_id: str) -> Response:
        """
        This is the documentation for /api/v1/report/drivers/<string:driver_id>/
         endpoint

         GET:
         This operation retrieves a statistic of driver by provided driver_id
         ---
         parameters:
           - name: driver_id
             in: path
             type: string
             required: True
             description: The unique identifier of the driver
           - name: format
             in: query
             type: string
             enum: ['json', 'xml']
             default: 'json'

         responses:
           200:
             descriptions: Return statistic of unique driver
             schema:
               type: object
               properties:
                 data:
                   type: string

           404:
             descriptions: Driver not found, return an error page
        """
        args = parser.parse_args()
        for driver in PREPARED_DATA:
            if driver.abr == driver_id:

                if args['format'] == 'xml':
                    return xml_response_api_driver(driver)

                return json_response_api_driver(driver)

        return make_response(render_template('404.html'), 404)
