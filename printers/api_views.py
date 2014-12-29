'''Api views for printers app'''
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import permissions

from printers.models import Option,\
                            Printer,\
                            PrinterList#,\
                            # SubscriptionPrinterList

from printers.api_serializers import OptionSerializer, PrinterSerializer, PrinterListSerializer
# from printers.permissions import IsOwnerOrReadOnly


class OptionViewSet(viewsets.ReadOnlyModelViewSet):

    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    queryset = Option.objects.all()
    serializer_class = OptionSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        '''this is docstring'''
        return Option.objects.all()


class PrinterViewSet(viewsets.ReadOnlyModelViewSet):

    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',
                     'location',
                     'description')

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        '''this is docstring'''
        return Printer.objects.all()


class PrinterListViewSet(viewsets.ReadOnlyModelViewSet):

    '''
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    '''

    queryset = PrinterList.objects.all()
    serializer_class = PrinterListSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',
                     'printers',
                     'public')

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        '''Get the printer list query set for the view set'''
        return PrinterList.objects.all()
