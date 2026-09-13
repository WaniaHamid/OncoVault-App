import 'package:flutter_test/flutter_test.dart';
import 'package:oncovault/models/nlp_extraction_model.dart';
import 'package:oncovault/models/blood_cancer_ehr_model.dart';

void main() {
  group('NlpExtractionModel Tests', () {
    test('parses extraction response JSON properly', () {
      final jsonMap = {
        'text': 'Patient has persistent fatigue and fever but denies bone pain. WBC is 14.5 k/uL, hemoglobin is 10.2 g/dL and platelets are 110 k/uL.',
        'symptoms': {
          'persistentWeaknessAndFatigue': {
            'value': true,
            'status': 'present',
            'source_text': 'persistent fatigue',
          },
          'fever': {
            'value': true,
            'status': 'present',
            'source_text': 'fever',
          },
          'bonePain': {
            'value': false,
            'status': 'negated',
            'source_text': 'denies bone pain',
          },
        },
        'cbc': {
          'wbc': {
            'value': 14.5,
            'unit': 'k/uL',
            'status': 'present',
            'source_text': 'WBC is 14.5 k/uL',
          },
          'hemoglobin': {
            'value': 10.2,
            'unit': 'g/dL',
            'status': 'present',
            'source_text': 'hemoglobin is 10.2 g/dL',
          },
          'platelets': {
            'value': 110.0,
            'unit': 'k/uL',
            'status': 'present',
            'source_text': 'platelets are 110 k/uL',
          },
          'neutrophils': {
            'absolute': 4.5,
            'percentage': 60.0,
            'source_text': 'neutrophils 4.5 k/uL (60%)',
          },
        },
        'other': {
          'diseaseType': 'Acute Leukemia',
          'diagnosisSubtype': 'AML',
          'stage': 'Intermediate',
          'diagnosisStatus': 'Active',
          'blastCellPercentage': 12.0,
          'chemotherapy': '7+3',
          'clinicalNotes': 'Patient evaluation',
        },
        'warnings': <String>[],
      };

      final response = NlpExtractionResponse.fromMap(jsonMap);

      expect(response.text, equals(jsonMap['text']));
      expect(response.symptoms['persistentWeaknessAndFatigue']?.value, isTrue);
      expect(response.symptoms['persistentWeaknessAndFatigue']?.status, equals('present'));
      expect(response.symptoms['bonePain']?.value, isFalse);
      expect(response.symptoms['bonePain']?.status, equals('negated'));

      expect(response.cbc.wbc?.value, equals(14.5));
      expect(response.cbc.wbc?.unit, equals('k/uL'));
      expect(response.cbc.hemoglobin?.value, equals(10.2));
      expect(response.cbc.platelets?.value, equals(110.0));
      expect(response.cbc.neutrophils?.absolute, equals(4.5));
      expect(response.cbc.neutrophils?.percentage, equals(60.0));

      expect(response.other.diseaseType, equals('Acute Leukemia'));
      expect(response.other.diagnosisSubtype, equals('AML'));
      expect(response.other.blastCellPercentage, equals(12.0));
      expect(response.other.chemotherapy, equals('7+3'));
    });

    test('BloodCancerEhrModel maps correctly with extracted data', () {
      const symptoms = BloodCancerSymptoms(
        fever: true,
        persistentWeaknessAndFatigue: true,
        bonePain: false,
      );

      const cbc = BloodCancerCbc(
        wbc: 14.5,
        hemoglobin: 10.2,
        platelets: 110.0,
      );

      final ehr = BloodCancerEhrModel(
        recordId: 'rec_123',
        patientId: 'pat_456',
        patientName: 'Test Patient',
        doctorId: 'doc_789',
        doctorName: 'Dr. Smith',
        createdAt: DateTime(2026, 9, 1),
        symptoms: symptoms,
        cbc: cbc,
        diseaseType: 'Acute Leukemia',
        diagnosisSubtype: 'AML',
      );

      expect(ehr.symptoms.fever, isTrue);
      expect(ehr.symptoms.bonePain, isFalse);
      expect(ehr.cbc.wbc, equals(14.5));
      expect(ehr.cbc.hemoglobin, equals(10.2));
      expect(ehr.cbc.platelets, equals(110.0));
      expect(ehr.diseaseType, equals('Acute Leukemia'));
    });
  });
}
