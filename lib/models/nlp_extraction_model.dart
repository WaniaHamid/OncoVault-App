// lib/models/nlp_extraction_model.dart

class SymptomExtractionResult {
  final bool value;
  final String status;
  final String? sourceText;
  final double? confidence;

  const SymptomExtractionResult({
    required this.value,
    required this.status,
    this.sourceText,
    this.confidence,
  });

  factory SymptomExtractionResult.fromMap(Map<String, dynamic> map) {
    return SymptomExtractionResult(
      value: map['value'] as bool? ?? false,
      status: map['status'] as String? ?? 'present',
      sourceText: map['source_text'] as String?,
      confidence: (map['confidence'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toMap() => {
    'value': value,
    'status': status,
    'source_text': sourceText,
    'confidence': confidence,
  };

  SymptomExtractionResult copyWith({
    bool? value,
    String? status,
    String? sourceText,
    double? confidence,
  }) {
    return SymptomExtractionResult(
      value: value ?? this.value,
      status: status ?? this.status,
      sourceText: sourceText ?? this.sourceText,
      confidence: confidence ?? this.confidence,
    );
  }
}

class CbcValueResult {
  final double? value;
  final String? unit;
  final String status;
  final String? sourceText;

  const CbcValueResult({
    this.value,
    this.unit,
    this.status = 'present',
    this.sourceText,
  });

  factory CbcValueResult.fromMap(Map<String, dynamic>? map) {
    if (map == null) return const CbcValueResult();
    return CbcValueResult(
      value: (map['value'] as num?)?.toDouble(),
      unit: map['unit'] as String?,
      status: map['status'] as String? ?? 'present',
      sourceText: map['source_text'] as String?,
    );
  }

  Map<String, dynamic> toMap() => {
    'value': value,
    'unit': unit,
    'status': status,
    'source_text': sourceText,
  };

  CbcValueResult copyWith({
    double? value,
    String? unit,
    String? status,
    String? sourceText,
  }) {
    return CbcValueResult(
      value: value ?? this.value,
      unit: unit ?? this.unit,
      status: status ?? this.status,
      sourceText: sourceText ?? this.sourceText,
    );
  }
}

class DifferentialCountResult {
  final double? absolute;
  final double? percentage;
  final String? sourceText;

  const DifferentialCountResult({
    this.absolute,
    this.percentage,
    this.sourceText,
  });

  factory DifferentialCountResult.fromMap(Map<String, dynamic>? map) {
    if (map == null) return const DifferentialCountResult();
    return DifferentialCountResult(
      absolute: (map['absolute'] as num?)?.toDouble(),
      percentage: (map['percentage'] as num?)?.toDouble(),
      sourceText: map['source_text'] as String?,
    );
  }

  Map<String, dynamic> toMap() => {
    'absolute': absolute,
    'percentage': percentage,
    'source_text': sourceText,
  };

  DifferentialCountResult copyWith({
    double? absolute,
    double? percentage,
    String? sourceText,
  }) {
    return DifferentialCountResult(
      absolute: absolute ?? this.absolute,
      percentage: percentage ?? this.percentage,
      sourceText: sourceText ?? this.sourceText,
    );
  }
}

class CbcExtractionResult {
  final CbcValueResult? wbc;
  final CbcValueResult? rbc;
  final CbcValueResult? hemoglobin;
  final CbcValueResult? hematocrit;
  final CbcValueResult? platelets;
  final DifferentialCountResult? neutrophils;
  final DifferentialCountResult? lymphocytes;
  final DifferentialCountResult? monocytes;
  final DifferentialCountResult? eosinophils;
  final DifferentialCountResult? basophils;
  final CbcValueResult? rdwSd;
  final CbcValueResult? rdwCv;

  const CbcExtractionResult({
    this.wbc,
    this.rbc,
    this.hemoglobin,
    this.hematocrit,
    this.platelets,
    this.neutrophils,
    this.lymphocytes,
    this.monocytes,
    this.eosinophils,
    this.basophils,
    this.rdwSd,
    this.rdwCv,
  });

  factory CbcExtractionResult.fromMap(Map<String, dynamic>? map) {
    if (map == null) return const CbcExtractionResult();
    return CbcExtractionResult(
      wbc: map['wbc'] != null ? CbcValueResult.fromMap(map['wbc'] as Map<String, dynamic>) : null,
      rbc: map['rbc'] != null ? CbcValueResult.fromMap(map['rbc'] as Map<String, dynamic>) : null,
      hemoglobin: map['hemoglobin'] != null ? CbcValueResult.fromMap(map['hemoglobin'] as Map<String, dynamic>) : null,
      hematocrit: map['hematocrit'] != null ? CbcValueResult.fromMap(map['hematocrit'] as Map<String, dynamic>) : null,
      platelets: map['platelets'] != null ? CbcValueResult.fromMap(map['platelets'] as Map<String, dynamic>) : null,
      neutrophils: map['neutrophils'] != null ? DifferentialCountResult.fromMap(map['neutrophils'] as Map<String, dynamic>) : null,
      lymphocytes: map['lymphocytes'] != null ? DifferentialCountResult.fromMap(map['lymphocytes'] as Map<String, dynamic>) : null,
      monocytes: map['monocytes'] != null ? DifferentialCountResult.fromMap(map['monocytes'] as Map<String, dynamic>) : null,
      eosinophils: map['eosinophils'] != null ? DifferentialCountResult.fromMap(map['eosinophils'] as Map<String, dynamic>) : null,
      basophils: map['basophils'] != null ? DifferentialCountResult.fromMap(map['basophils'] as Map<String, dynamic>) : null,
      rdwSd: map['rdwSd'] != null ? CbcValueResult.fromMap(map['rdwSd'] as Map<String, dynamic>) : null,
      rdwCv: map['rdwCv'] != null ? CbcValueResult.fromMap(map['rdwCv'] as Map<String, dynamic>) : null,
    );
  }

  Map<String, dynamic> toMap() => {
    'wbc': wbc?.toMap(),
    'rbc': rbc?.toMap(),
    'hemoglobin': hemoglobin?.toMap(),
    'hematocrit': hematocrit?.toMap(),
    'platelets': platelets?.toMap(),
    'neutrophils': neutrophils?.toMap(),
    'lymphocytes': lymphocytes?.toMap(),
    'monocytes': monocytes?.toMap(),
    'eosinophils': eosinophils?.toMap(),
    'basophils': basophils?.toMap(),
    'rdwSd': rdwSd?.toMap(),
    'rdwCv': rdwCv?.toMap(),
  };

  CbcExtractionResult copyWith({
    CbcValueResult? wbc,
    CbcValueResult? rbc,
    CbcValueResult? hemoglobin,
    CbcValueResult? hematocrit,
    CbcValueResult? platelets,
    DifferentialCountResult? neutrophils,
    DifferentialCountResult? lymphocytes,
    DifferentialCountResult? monocytes,
    DifferentialCountResult? eosinophils,
    DifferentialCountResult? basophils,
    CbcValueResult? rdwSd,
    CbcValueResult? rdwCv,
  }) {
    return CbcExtractionResult(
      wbc: wbc ?? this.wbc,
      rbc: rbc ?? this.rbc,
      hemoglobin: hemoglobin ?? this.hemoglobin,
      hematocrit: hematocrit ?? this.hematocrit,
      platelets: platelets ?? this.platelets,
      neutrophils: neutrophils ?? this.neutrophils,
      lymphocytes: lymphocytes ?? this.lymphocytes,
      monocytes: monocytes ?? this.monocytes,
      eosinophils: eosinophils ?? this.eosinophils,
      basophils: basophils ?? this.basophils,
      rdwSd: rdwSd ?? this.rdwSd,
      rdwCv: rdwCv ?? this.rdwCv,
    );
  }
}

class OtherClinicalResult {
  final String? diseaseType;
  final String? diagnosisSubtype;
  final String? stage;
  final String? diagnosisStatus;
  final double? blastCellPercentage;
  final String? boneMarrowBiopsy;
  final String? chemotherapy;
  final List<String> medications;
  final String? clinicalNotes;

  const OtherClinicalResult({
    this.diseaseType,
    this.diagnosisSubtype,
    this.stage,
    this.diagnosisStatus,
    this.blastCellPercentage,
    this.boneMarrowBiopsy,
    this.chemotherapy,
    this.medications = const [],
    this.clinicalNotes,
  });

  factory OtherClinicalResult.fromMap(Map<String, dynamic>? map) {
    if (map == null) return const OtherClinicalResult();
    List<String> meds = [];
    if (map['medications'] is List) {
      meds = (map['medications'] as List).map((e) => e.toString()).toList();
    }
    return OtherClinicalResult(
      diseaseType: map['diseaseType'] as String?,
      diagnosisSubtype: map['diagnosisSubtype'] as String?,
      stage: map['stage'] as String?,
      diagnosisStatus: map['diagnosisStatus'] as String?,
      blastCellPercentage: (map['blastCellPercentage'] as num?)?.toDouble(),
      boneMarrowBiopsy: map['boneMarrowBiopsy'] as String?,
      chemotherapy: map['chemotherapy'] as String?,
      medications: meds,
      clinicalNotes: map['clinicalNotes'] as String?,
    );
  }

  Map<String, dynamic> toMap() => {
    'diseaseType': diseaseType,
    'diagnosisSubtype': diagnosisSubtype,
    'stage': stage,
    'diagnosisStatus': diagnosisStatus,
    'blastCellPercentage': blastCellPercentage,
    'boneMarrowBiopsy': boneMarrowBiopsy,
    'chemotherapy': chemotherapy,
    'medications': medications,
    'clinicalNotes': clinicalNotes,
  };
}

class NlpExtractionResponse {
  final String text;
  final Map<String, SymptomExtractionResult> symptoms;
  final CbcExtractionResult cbc;
  final OtherClinicalResult other;
  final List<String> warnings;

  const NlpExtractionResponse({
    required this.text,
    this.symptoms = const {},
    this.cbc = const CbcExtractionResult(),
    this.other = const OtherClinicalResult(),
    this.warnings = const [],
  });

  factory NlpExtractionResponse.fromMap(Map<String, dynamic> map) {
    final symMap = <String, SymptomExtractionResult>{};
    if (map['symptoms'] is Map) {
      final rawSym = map['symptoms'] as Map<String, dynamic>;
      rawSym.forEach((k, v) {
        if (v is Map<String, dynamic>) {
          symMap[k] = SymptomExtractionResult.fromMap(v);
        }
      });
    }

    final cbcRes = map['cbc'] != null
        ? CbcExtractionResult.fromMap(map['cbc'] as Map<String, dynamic>)
        : const CbcExtractionResult();

    final otherRes = map['other'] != null
        ? OtherClinicalResult.fromMap(map['other'] as Map<String, dynamic>)
        : const OtherClinicalResult();

    List<String> warnList = [];
    if (map['warnings'] is List) {
      warnList = (map['warnings'] as List).map((e) => e.toString()).toList();
    }

    return NlpExtractionResponse(
      text: map['text'] as String? ?? '',
      symptoms: symMap,
      cbc: cbcRes,
      other: otherRes,
      warnings: warnList,
    );
  }
}
