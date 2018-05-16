from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

import os

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from djangorestframework_camel_case.parser import CamelCaseJSONParser

from core.layout.generate import generate_layout
from core.layout.optimize.optimize import optimize
from core.layout.util import calculate_layout_width
from exceptions.exceptions import NO_FILE_ERROR, ILLEGAL_EDIT_TOKEN_ERROR, LAYOUT_ALREADY_EDITED_ERROR, \
    NO_EDIT_TOKEN_ERROR, ALREADY_INITED_ERROR, ILLEGAL_EDIT_MODE_OFF_ERROR
from exceptions.serializers import ErrorMessageSerializer
from exceptions.structs import ErrorMessage
from exceptions.util import message_from_serializer_errors
from layouts.serializers import ShortLayoutDataSerializer, FullLayoutDataSerializer
from layouts.structs import LayoutData
from layouts.util import generate_unique_filename, generate_edit_token, check_layouts_dates_equality, \
    update_out_of_order, update_required_fields

from layouts.db.save import save_new_layout_to_db, save_layout_priorities
from layouts.db.get import get_layout_from_db, get_layout_relations_from_db
from layouts.db.update import update_layout_in_db

from .models import Layout


INIT_FILES_PATH = 'init_files'
CURRENT_FILE_PATH = os.path.join('current_file', 'current.xlsx')
EDIT_TOKEN_HEADER = 'HTTP_EDIT_TOKEN'


class LayoutsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        layouts = Layout.objects.all()
        data = ShortLayoutDataSerializer(layouts, many=True).data
        return Response({'layouts': data}, status=status.HTTP_200_OK)

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        data = CamelCaseJSONParser().parse(request)
        serializer = ShortLayoutDataSerializer(data=data)
        if serializer.is_valid():
            layout, priorities = serializer.save()
            layout.width = calculate_layout_width(layout.duration_limit)
            layout.save()
            save_layout_priorities(layout, priorities)
            return Response(ShortLayoutDataSerializer(layout).data, status=status.HTTP_200_OK)
        return Response(ErrorMessageSerializer(message_from_serializer_errors(serializer.errors)).data,
                        status=status.HTTP_400_BAD_REQUEST)


class LayoutView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        layout_obj = get_layout_from_db(layout)
        layout_data = LayoutData.from_layout(layout_obj)
        return Response(FullLayoutDataSerializer(layout_data).data, status=status.HTTP_200_OK)

    @csrf_exempt
    def delete(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        filename = layout.filename
        layout.delete()
        delete_file_if_exists(filename)
        return Response({}, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        data = CamelCaseJSONParser().parse(request)
        serializer = FullLayoutDataSerializer(data=data)
        try:
            check_in_edit_mode(request, layout)
            if serializer.is_valid():
                layout_data = serializer.save()
                update_layout_in_db(layout_data, layout)
                layout_obj = get_layout_from_db(layout)
                layout_data = LayoutData.from_layout(layout_obj)
                return Response(FullLayoutDataSerializer(layout_data).data, status=status.HTTP_200_OK)
            raise message_from_serializer_errors(serializer.errors)
        except ErrorMessage as e:
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)


class UpdateLayoutFromFileMixin(object):

    def _update_layout(self, layout: Layout, new_filename: str, save_filename: bool=True, from_current: bool=False):
        layout_obj = get_layout_from_db(layout)
        full_filename = new_filename if from_current else os.path.join(INIT_FILES_PATH, new_filename)
        new_layout_obj = generate_layout(full_filename, layout_obj.min_days,
                                         layout_obj.max_days, layout_obj.duration_limit, layout_obj.relations,
                                         layout_obj.width, layout_obj.name, layout_obj.id)
        check_layouts_dates_equality(layout_obj, new_layout_obj)
        update_out_of_order(new_layout_obj, layout_obj.out_of_order)
        update_required_fields(new_layout_obj, layout_obj)
        new_layout_obj.date_relations = layout_obj.date_relations
        new_layout_obj.no_losses = layout_obj.no_losses
        optimize(new_layout_obj)
        prev_filename = layout.filename
        update_layout_in_db(LayoutData.from_layout(new_layout_obj), layout, new_filename if save_filename else None,
                            update_last_update=True)
        delete_file_if_exists(prev_filename)
        layout_data = LayoutData.from_layout(get_layout_from_db(layout))
        return layout_data


class LayoutInitView(APIView, UpdateLayoutFromFileMixin):

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    def post(self, request, pk, format=None):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        filename = None
        try:
            if layout.start_date is not None and layout.end_date is not None:
                raise ALREADY_INITED_ERROR
            filename = save_init_file(request)
            layout.filename = filename
            relations = get_layout_relations_from_db(layout)
            layout_obj = generate_layout(os.path.join(INIT_FILES_PATH, filename), layout.min_days, layout.max_days,
                                         layout.duration_limit, relations, layout.width, layout.name, layout.id)
            optimize(layout_obj)
            save_new_layout_to_db(layout_obj, layout)
            layout_data = LayoutData.from_layout(layout_obj)
            return Response(FullLayoutDataSerializer(layout_data).data, status=status.HTTP_200_OK)
        except ErrorMessage as e:
            delete_file_if_exists(filename)
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    def put(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        new_filename = None
        try:
            check_in_edit_mode(request, layout)
            new_filename = save_init_file(request)
            layout_data = self._update_layout(layout, new_filename)
            return Response(FullLayoutDataSerializer(layout_data).data, status=status.HTTP_200_OK)
        except ErrorMessage as e:
            delete_file_if_exists(new_filename)
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)


class LayoutUpdateFromCurrentFileView(APIView, UpdateLayoutFromFileMixin):

    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    def post(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        try:
            check_in_edit_mode(request, layout)
            layout_data = self._update_layout(layout, CURRENT_FILE_PATH, save_filename=False, from_current=True)
            return Response(FullLayoutDataSerializer(layout_data).data, status=status.HTTP_200_OK)
        except ErrorMessage as e:
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)


class LayoutPrecomputeView(APIView):

    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    def post(self, request):
        try:
            data = CamelCaseJSONParser().parse(request)
            serializer = FullLayoutDataSerializer(data=data)
            if serializer.is_valid():
                layout_data = serializer.save()
                layout_obj = layout_data.to_layout()
                optimize(layout_obj, layout_obj.update_date)
                layout_data = LayoutData.from_layout(layout_obj)
                return Response(FullLayoutDataSerializer(layout_data).data, status=status.HTTP_200_OK)
            raise message_from_serializer_errors(serializer.errors)
        except ErrorMessage as e:
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)


class LayoutRefreshEditTokenView(APIView):

    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    @transaction.atomic
    def post(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        try:
            edit_token = get_edit_token(request)
            is_edited = layout_is_edited(layout)
            if edit_token is not None and is_edited and edit_token == layout.edit_token:
                layout.last_token_update = timezone.now()
                layout.save()
                return Response({}, status=status.HTTP_200_OK)
            if edit_token is not None and (not is_edited or edit_token != layout.edit_token):
                raise ILLEGAL_EDIT_TOKEN_ERROR
            if edit_token is None and is_edited:
                raise LAYOUT_ALREADY_EDITED_ERROR
            new_token = generate_edit_token()
            layout.edit_token = new_token
            layout.last_token_update = timezone.now()
            layout.save()
            return Response({'token': new_token}, status=status.HTTP_200_OK)
        except ErrorMessage as e:
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @transaction.atomic
    def delete(self, request, pk):
        try:
            layout = Layout.objects.get(pk=pk)
        except Layout.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        try:
            edit_token = get_edit_token(request)
            is_edited = layout_is_edited(layout)
            if edit_token is not None and is_edited and edit_token == layout.edit_token:
                layout.last_token_update = None
                layout.edit_token = None
                layout.save()
                return Response({}, status=status.HTTP_200_OK)
            raise ILLEGAL_EDIT_MODE_OFF_ERROR
        except ErrorMessage as e:
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)


class SaveCurrentFileView(APIView):

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    def post(self, request, format=None):
        try:
            save_init_file(request, is_current_file=True)
            return Response({}, status=status.HTTP_200_OK)
        except ErrorMessage as e:
            return Response(ErrorMessageSerializer(e).data, status=status.HTTP_400_BAD_REQUEST)


def get_edit_token(request):
    return request.META[EDIT_TOKEN_HEADER] if EDIT_TOKEN_HEADER in request.META else None


def layout_is_edited(layout: Layout):
    if layout.last_token_update is None:
        return False
    return (timezone.now() - layout.last_token_update).total_seconds() < 60


def check_in_edit_mode(request, layout):
    is_edited = layout_is_edited(layout)
    edit_token = get_edit_token(request)
    if edit_token is None:
        raise NO_EDIT_TOKEN_ERROR
    if not is_edited or edit_token != layout.edit_token:
        raise ILLEGAL_EDIT_TOKEN_ERROR


def delete_file_if_exists(filename):
    if filename is None:
        return
    try:
        os.remove(os.path.join(INIT_FILES_PATH, filename))
    except OSError:
        pass


def save_init_file(request, is_current_file=False):
    try:
        file_obj = request.data['file']
    except KeyError:
        raise NO_FILE_ERROR
    if is_current_file:
        filename, fullname = CURRENT_FILE_PATH, CURRENT_FILE_PATH
    else:
        filename = generate_unique_filename(file_obj.name)
        fullname = os.path.join(INIT_FILES_PATH, filename)
    with open(fullname, 'wb') as dst:
        for chunk in file_obj.chunks():
            dst.write(chunk)
    return filename
