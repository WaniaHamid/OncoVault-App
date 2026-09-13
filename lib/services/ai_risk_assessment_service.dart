// lib/services/ai_risk_assessment_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/blood_cancer_ehr_model.dart';

/// Structured response from the OncoVault AI Diagnostic Decision Support Engine.
class AiRiskResult {
  final String prediction;
  final double riskScore;
  final String modelVersion;
  final List<String> contributingFactors;
  final DateTime analyzedAt;
  final String disclaimer;

  const AiRiskResult({
    required this.prediction,
    required this.riskScore,
    required this.modelVersion,
    required this.contributingFactors,
    required this.analyzedAt,
    required this.disclaimer,
  });

  bool get isElevatedRisk =>
      prediction.toLowerCase().contains('elevated') || riskScore >= 0.50;

  String get formattedPercentage => '${(riskScore * 100).toStringAsFixed(1)}%';

  factory AiRiskResult.fromJson(Map<String, dynamic> json) {
    return AiRiskResult(
      prediction: json['prediction'] as String? ?? 'Lower Risk',
      riskScore: (json['riskScore'] as num?)?.toDouble() ?? 0.0,
      modelVersion: json['modelVersion'] as String? ?? 'v1.0',
      contributingFactors: (json['contributingFactors'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      analyzedAt: json['analyzedAt'] != null
          ? DateTime.tryParse(json['analyzedAt'].toString()) ?? DateTime.now()
          : DateTime.now(),
      disclaimer: json['disclaimer'] as String? ??
          'AI risk assessment is for clinical decision support and is not a definitive diagnosis.',
    );
  }

  Map<String, dynamic> toJson() => {
        'prediction': prediction,
        'riskScore': riskScore,
        'modelVersion': modelVersion,
        'contributingFactors': contributingFactors,
        'analyzedAt': analyzedAt.toIso8601String(),
        'disclaimer': disclaimer,
      };
}

class AiRiskAssessmentService {
  final http.Client _client;

  AiRiskAssessmentService({http.Client? client})
      : _client = client ?? http.Client();

  /// Evaluates leukemia risk based on the 16 finalized clinical symptoms.
  Future<AiRiskResult> assessSymptoms(BloodCancerSymptoms symptoms) async {
    final url = Uri.parse(ApiConfig.predictSymptomsEndpoint);
    final payload = symptoms.toMap();

    try {
      final response = await _client
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(payload),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body) as Map<String, dynamic>;
        return AiRiskResult.fromJson(decoded);
      } else {
        throw Exception(
            'Symptom assessment failed [HTTP ${response.statusCode}]: ${response.body}');
      }
    } catch (e) {
      // Offline fallback: heuristic fallback if backend service is unreachable
      return _heuristicSymptomFallback(symptoms, errorNote: e.toString());
    }
  }

  /// Evaluates leukemia risk based on the 9 finalized CBC parameters.
  Future<AiRiskResult> assessCbc(BloodCancerCbc cbc) async {
    final url = Uri.parse(ApiConfig.predictCbcEndpoint);
    final payload = {
      'WBC': cbc.wbc,
      'RBC': cbc.rbc,
      'HGB': cbc.hemoglobin,
      'PLT': cbc.platelets,
      'NEUT_ABS': cbc.neutrophils?.absolute,
      'NEUT_PCT': cbc.neutrophils?.percentage,
      'MONO_ABS': cbc.monocytes?.absolute,
      'RDW_SD': cbc.rdwSd,
      'RDW_CV': cbc.rdwCv,
    };

    try {
      final response = await _client
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(payload),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body) as Map<String, dynamic>;
        return AiRiskResult.fromJson(decoded);
      } else {
        throw Exception(
            'CBC assessment failed [HTTP ${response.statusCode}]: ${response.body}');
      }
    } catch (e) {
      return _heuristicCbcFallback(cbc, errorNote: e.toString());
    }
  }

  AiRiskResult _heuristicSymptomFallback(BloodCancerSymptoms symptoms,
      {required String errorNote}) {
    int count = 0;
    List<String> keyFactors = [];

    if (symptoms.swollenPainlessLymphNodes == true) {
      count += 2;
      keyFactors.add('Swollen Painless Lymph Nodes');
    }
    if (symptoms.frequentInfections == true) {
      count += 2;
      keyFactors.add('Frequent Infections');
    }
    if (symptoms.enlargedLiver == true) {
      count += 2;
      keyFactors.add('Enlarged Liver / Hepatomegaly');
    }
    if (symptoms.bonePain == true) {
      count += 2;
      keyFactors.add('Bone Pain');
    }
    if (symptoms.persistentWeaknessAndFatigue == true) {
      count += 1;
      keyFactors.add('Persistent Weakness & Fatigue');
    }
    if (symptoms.significantBruisingOrBleeding == true) {
      count += 1;
      keyFactors.add('Significant Bruising / Bleeding');
    }

    final score = (count / 10.0).clamp(0.05, 0.95);
    return AiRiskResult(
      prediction: score >= 0.50 ? 'Elevated Risk' : 'Lower Risk',
      riskScore: score,
      modelVersion: 'leukemia-symptom-v1 (Offline Heuristic)',
      contributingFactors:
          keyFactors.isEmpty ? ['No major acute symptoms reported'] : keyFactors,
      analyzedAt: DateTime.now(),
      disclaimer:
          'Decision-support heuristic (Backend offline: $errorNote). Must be verified by clinician.',
    );
  }

  AiRiskResult _heuristicCbcFallback(BloodCancerCbc cbc,
      {required String errorNote}) {
    List<String> factors = [];
    double score = 0.20;

    if (cbc.platelets != null && cbc.platelets! < 100.0) {
      score += 0.35;
      factors.add('Thrombocytopenia (PLT: ${cbc.platelets} 10^9/L)');
    }
    if (cbc.wbc != null && (cbc.wbc! > 25.0 || cbc.wbc! < 3.0)) {
      score += 0.30;
      factors.add('Leukocyte Abnormality (WBC: ${cbc.wbc} 10^9/L)');
    }
    if (cbc.hemoglobin != null && cbc.hemoglobin! < 90.0) {
      score += 0.15;
      factors.add('Anemia (HGB: ${cbc.hemoglobin} g/L)');
    }

    score = score.clamp(0.05, 0.95);
    return AiRiskResult(
      prediction: score >= 0.50 ? 'Elevated Risk' : 'Lower Risk',
      riskScore: score,
      modelVersion: 'leukemia-cbc-v1 (Offline Heuristic)',
      contributingFactors:
          factors.isEmpty ? ['Normal reference indices'] : factors,
      analyzedAt: DateTime.now(),
      disclaimer:
          'Decision-support heuristic (Backend offline: $errorNote). Must be verified by clinician.',
    );
  }
}
