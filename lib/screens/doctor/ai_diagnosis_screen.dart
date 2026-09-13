// lib/screens/doctor/ai_diagnosis_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/app_theme.dart';
import '../../models/blood_cancer_ehr_model.dart';
import '../../services/ai_risk_assessment_service.dart';
import '../../services/doctor_service.dart';
import 'doctor_widgets.dart';

class AiDiagnosisScreen extends StatefulWidget {
  final String patientId, patientName;
  final BloodCancerEhrModel? initialEhr;

  const AiDiagnosisScreen({
    super.key,
    required this.patientId,
    required this.patientName,
    this.initialEhr,
  });

  @override
  State<AiDiagnosisScreen> createState() => _AiDiagnosisScreenState();
}

class _AiDiagnosisScreenState extends State<AiDiagnosisScreen>
    with SingleTickerProviderStateMixin {
  final AiRiskAssessmentService _aiService = AiRiskAssessmentService();
  final DoctorService _doctorService = DoctorService();

  BloodCancerEhrModel? _ehr;
  bool _loadingEhr = true;
  bool _assessingSymptoms = false;
  bool _assessingCbc = false;
  bool _savingReview = false;

  AiRiskResult? _symptomResult;
  AiRiskResult? _cbcResult;

  @override
  void initState() {
    super.initState();
    _loadPatientEhr();
  }

  Future<void> _loadPatientEhr() async {
    if (widget.initialEhr != null) {
      _ehr = widget.initialEhr;
      setState(() => _loadingEhr = false);
      return;
    }

    setState(() => _loadingEhr = true);
    try {
      _ehr = await _doctorService.fetchLatestBloodCancerEhr(widget.patientId);
    } catch (e) {
      debugPrint('Error loading EHR: $e');
    } finally {
      if (mounted) {
        setState(() => _loadingEhr = false);
      }
    }
  }

  Future<void> _runSymptomAssessment() async {
    final symptoms = _ehr?.symptoms ?? const BloodCancerSymptoms();
    setState(() => _assessingSymptoms = true);

    try {
      final result = await _aiService.assessSymptoms(symptoms);
      if (mounted) {
        setState(() {
          _symptomResult = result;
          _assessingSymptoms = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _assessingSymptoms = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Symptom assessment error: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  Future<void> _runCbcAssessment() async {
    final cbc = _ehr?.cbc ?? const BloodCancerCbc();
    setState(() => _assessingCbc = true);

    try {
      final result = await _aiService.assessCbc(cbc);
      if (mounted) {
        setState(() {
          _cbcResult = result;
          _assessingCbc = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _assessingCbc = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('CBC assessment error: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  Future<void> _runBothAssessments() async {
    await Future.wait([
      _runSymptomAssessment(),
      _runCbcAssessment(),
    ]);
  }

  Future<void> _saveDoctorReview() async {
    if (_symptomResult == null && _cbcResult == null) return;
    setState(() => _savingReview = true);

    try {
      String prediction;
      double riskScore;
      String modelVersion;

      if (_cbcResult != null && _symptomResult != null) {
        prediction = 'CBC: ${_cbcResult!.prediction} (${(_cbcResult!.riskScore * 100).toStringAsFixed(1)}%) | Symptoms: ${_symptomResult!.prediction} (${(_symptomResult!.riskScore * 100).toStringAsFixed(1)}%)';
        riskScore = _cbcResult!.riskScore > _symptomResult!.riskScore ? _cbcResult!.riskScore : _symptomResult!.riskScore;
        modelVersion = '${_cbcResult!.modelVersion} & ${_symptomResult!.modelVersion}';
      } else if (_cbcResult != null) {
        prediction = 'CBC: ${_cbcResult!.prediction} (${(_cbcResult!.riskScore * 100).toStringAsFixed(1)}%)';
        riskScore = _cbcResult!.riskScore;
        modelVersion = _cbcResult!.modelVersion;
      } else {
        prediction = 'Symptoms: ${_symptomResult!.prediction} (${(_symptomResult!.riskScore * 100).toStringAsFixed(1)}%)';
        riskScore = _symptomResult!.riskScore;
        modelVersion = _symptomResult!.modelVersion;
      }

      final updatedAi = AiAnalysisMetadata(
        prediction: prediction,
        riskScore: riskScore,
        modelVersion: modelVersion,
        analyzedAt: DateTime.now(),
        doctorReviewed: true,
      );

      var recordToSave = _ehr;
      if (recordToSave == null || recordToSave.recordId.isEmpty) {
        final latest = await _doctorService.fetchLatestBloodCancerEhr(widget.patientId);
        if (latest != null) {
          recordToSave = latest.copyWith(
            symptoms: _ehr?.symptoms ?? latest.symptoms,
            cbc: _ehr?.cbc ?? latest.cbc,
            aiAnalysis: updatedAi,
          );
        } else if (recordToSave != null) {
          recordToSave = recordToSave.copyWith(aiAnalysis: updatedAi);
        }
      } else {
        recordToSave = recordToSave.copyWith(aiAnalysis: updatedAi);
      }

      if (recordToSave != null) {
        await _doctorService.saveBloodCancerEhr(recordToSave);
      }

      if (mounted) {
        setState(() => _savingReview = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Doctor review confirmed and saved to patient EHR.'),
            backgroundColor: OV.primary,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _savingReview = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save review: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: OV.background,
      body: SafeArea(
        child: Column(
          children: [
            DoctorAppBar(
              title: 'AI Leukemia Risk Assessment',
              showBack: true,
            ),
            Expanded(
              child: _loadingEhr
                  ? const Center(child: CircularProgressIndicator())
                  : SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildPatientHeader(),
                          const SizedBox(height: 16),
                          _buildRunAllButton(),
                          const SizedBox(height: 20),
                          _buildSymptomCard(),
                          const SizedBox(height: 16),
                          _buildCbcCard(),
                          const SizedBox(height: 20),
                          _buildClinicalDisclaimer(),
                          const SizedBox(height: 20),
                          _buildDoctorReviewCard(),
                          const SizedBox(height: 30),
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPatientHeader() {
    return DCard(
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: OV.primaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.person_outline_rounded,
                color: OV.primary, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.patientName,
                  style: GoogleFonts.manrope(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: OV.onSurface,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'ID: ${widget.patientId} • Clinical Decision Support',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: OV.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRunAllButton() {
    final isRunning = _assessingSymptoms || _assessingCbc;
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton.icon(
        onPressed: isRunning ? null : _runBothAssessments,
        icon: isRunning
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : const Icon(Icons.auto_awesome_rounded, size: 20),
        label: Text(
          isRunning
              ? 'Calculating Risk Scores...'
              : 'Run Dual AI Risk Assessment',
          style: GoogleFonts.manrope(
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: OV.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
    );
  }

  Widget _buildSymptomCard() {
    return DCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFE8F5E9),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.checklist_rounded,
                    color: Color(0xFF2E7D32), size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Symptom Risk Model',
                      style: GoogleFonts.manrope(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: OV.onSurface,
                      ),
                    ),
                    Text(
                      '16 Clinical Symptoms • leukemia-symptom-v1',
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        color: OV.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              if (_assessingSymptoms)
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              else
                TextButton(
                  onPressed: _runSymptomAssessment,
                  style: TextButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                  child: Text(
                    _symptomResult == null ? 'Assess' : 'Re-assess',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: OV.primary,
                    ),
                  ),
                ),
            ],
          ),
          const Divider(height: 20),
          if (_symptomResult == null) ...[
            Text(
              'No symptom assessment generated yet. Click "Assess" to analyze the patient\'s 16 recorded symptoms.',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: OV.outline,
                height: 1.4,
              ),
            ),
          ] else ...[
            _buildResultBody(_symptomResult!),
          ],
        ],
      ),
    );
  }

  Widget _buildCbcCard() {
    return DCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFEDE7F6),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.biotech_rounded,
                    color: Color(0xFF512DA8), size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'CBC Risk Model',
                      style: GoogleFonts.manrope(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: OV.onSurface,
                      ),
                    ),
                    Text(
                      '9 CBC Parameters • leukemia-cbc-v1',
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        color: OV.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              if (_assessingCbc)
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              else
                TextButton(
                  onPressed: _runCbcAssessment,
                  style: TextButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                  child: Text(
                    _cbcResult == null ? 'Assess' : 'Re-assess',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: OV.primary,
                    ),
                  ),
                ),
            ],
          ),
          const Divider(height: 20),
          if (_cbcResult == null) ...[
            Text(
              'No CBC assessment generated yet. Click "Assess" to analyze the 9 finalized CBC parameters.',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: OV.outline,
                height: 1.4,
              ),
            ),
          ] else ...[
            _buildResultBody(_cbcResult!),
          ],
        ],
      ),
    );
  }

  Widget _buildResultBody(AiRiskResult result) {
    final isElevated = result.isElevatedRisk;
    final statusColor =
        isElevated ? const Color(0xFFC62828) : const Color(0xFF2E7D32);
    final statusBg =
        isElevated ? const Color(0xFFFFEBEE) : const Color(0xFFE8F5E9);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: statusBg,
                borderRadius: BorderRadius.circular(100),
                border: Border.all(color: statusColor.withOpacity(0.3)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    isElevated
                        ? Icons.warning_amber_rounded
                        : Icons.check_circle_outline_rounded,
                    color: statusColor,
                    size: 14,
                  ),
                  const SizedBox(width: 5),
                  Text(
                    result.prediction,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: statusColor,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              'Risk Score: ${result.formattedPercentage}',
              style: GoogleFonts.manrope(
                fontSize: 14,
                fontWeight: FontWeight.w800,
                color: statusColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            value: result.riskScore.clamp(0.0, 1.0),
            minHeight: 8,
            backgroundColor: OV.surfaceContainer,
            valueColor: AlwaysStoppedAnimation<Color>(statusColor),
          ),
        ),
        if (result.contributingFactors.isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(
            'KEY CONTRIBUTING FACTORS',
            style: GoogleFonts.inter(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.6,
              color: OV.outline,
            ),
          ),
          const SizedBox(height: 6),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: result.contributingFactors.map((f) {
              return Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: OV.surfaceLow,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: OV.outlineVariant),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.arrow_right_rounded,
                        size: 14, color: OV.primary),
                    Text(
                      f,
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: OV.onSurface,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ],
    );
  }

  Widget _buildClinicalDisclaimer() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF8E1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFFFD54F)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline_rounded,
              color: Color(0xFFF57F17), size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Clinical Decision Support Disclaimer',
                  style: GoogleFonts.manrope(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: const Color(0xFF5D4037),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'This AI system provides risk stratification to assist clinical judgment. It does not replace comprehensive pathological examination or specialist diagnosis. Symptom models are derived from pediatric cohort data.',
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    color: const Color(0xFF5D4037),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorReviewCard() {
    final canReview = _symptomResult != null || _cbcResult != null;

    return DCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Doctor-in-the-Loop Review',
            style: GoogleFonts.manrope(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: OV.onSurface,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Confirm review of AI risk scores and contributing factors. Approved assessments are permanently appended to the patient\'s EHR audit log.',
            style: GoogleFonts.inter(
              fontSize: 12,
              color: OV.onSurfaceVariant,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 46,
            child: ElevatedButton.icon(
              onPressed:
                  (!canReview || _savingReview) ? null : _saveDoctorReview,
              icon: _savingReview
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.verified_user_outlined, size: 18),
              label: Text(
                _savingReview
                    ? 'Saving Review...'
                    : 'Confirm Doctor Review & Save to EHR',
                style: GoogleFonts.manrope(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: OV.slateDark,
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
